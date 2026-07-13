"""Password hashing and JWT tokens.

Deliberate choice: this module calls `bcrypt` directly and does NOT use
`passlib`.

Almost every FastAPI auth tutorial reaches for passlib's CryptContext. passlib
1.7.4 is the last release, it is effectively unmaintained, and it breaks against
bcrypt >= 4.1: its version-detection code reads `bcrypt.__about__.__version__`,
an attribute modern bcrypt no longer has. The failure surfaces as a baffling
"password cannot be longer than 72 bytes" ValueError on a 5-character password.

This was reproduced before a line of auth code was written. Calling bcrypt
directly is simpler, one dependency lighter, and does not break.
"""

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from jose import JWTError, jwt

from backend.app.config import get_settings

settings = get_settings()

# bcrypt operates on at most 72 bytes and RAISES on anything longer - it does
# not truncate silently. So the API must reject over-long passwords before they
# reach the hasher, or registration 500s on a long passphrase.
MAX_PASSWORD_BYTES = 72


def hash_password(plain_password: str) -> str:
    """Hash a password with bcrypt.

    Cost factor 12 means 2^12 rounds of key derivation: fast enough that a
    legitimate login is imperceptible (~250 ms), slow enough that brute-forcing
    a stolen hash database is economically painful. bcrypt also salts every
    hash automatically, so two users with the same password get different
    hashes and precomputed rainbow tables are useless.
    """
    pw_bytes = plain_password.encode("utf-8")
    if len(pw_bytes) > MAX_PASSWORD_BYTES:
        raise ValueError(
            f"Password exceeds bcrypt's {MAX_PASSWORD_BYTES}-byte limit."
        )
    return bcrypt.hashpw(pw_bytes, bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a password against its stored hash.

    Returns False rather than raising on malformed input: a corrupt hash in the
    database is an auth failure, not a 500. And bcrypt.checkpw is a
    constant-time comparison, which is what stops an attacker learning the hash
    byte-by-byte from response timings.
    """
    try:
        pw_bytes = plain_password.encode("utf-8")
        if len(pw_bytes) > MAX_PASSWORD_BYTES:
            return False
        return bcrypt.checkpw(pw_bytes, hashed_password.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(
    subject: str,
    role: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Mint a signed JWT.

    The token carries the user's id and role, so most requests need no database
    lookup to authorise. That is the point of a JWT - and also its trade-off:
    a token is valid until it expires, so a role change or a deactivated account
    does not take effect until the current token dies. Hence a SHORT lifetime
    (30 minutes by default), and hence the `is_active` re-check in the
    get_current_user dependency for anything that actually matters.

    The token is SIGNED, not encrypted. Anyone can read its contents. Never put
    a secret in a JWT payload.
    """
    now = datetime.now(UTC)
    expire = now + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    payload: dict[str, Any] = {
        "sub": subject,   # standard claim: the subject (our user id)
        "role": role,     # custom claim: saves a DB hit on every request
        "exp": expire,    # standard claim: expiry. jose enforces this on decode
        "iat": now,       # standard claim: issued-at

        # A unique ID for THIS token. Without it, a token has no identity and
        # therefore cannot be revoked - you can only wait for it to expire. That
        # made /logout a lie: it deleted the token from the browser and left it
        # perfectly valid for anyone who had already copied it.
        "jti": str(uuid.uuid4()),

        # The token's TYPE, inside the signed payload.
        #
        # An access token and a refresh token are both JWTs signed with the same
        # key. Structurally they are indistinguishable. Without this claim, an
        # attacker who steals a 7-day refresh token can present it as an access
        # token and get 7 days of API access instead of a 15-minute window.
        "type": "access",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Verify and decode a JWT. Returns None if it is invalid or expired.

    `jwt.decode` verifies the signature AND the expiry. A token whose payload
    has been tampered with fails signature verification; an expired one raises.
    Both land in the same bucket: not a valid token.

    Note we pin `algorithms=` explicitly. Accepting whatever algorithm the token
    claims to use is the classic "alg: none" JWT vulnerability - an attacker
    hands you an unsigned token and a naive library accepts it.

    THIS NOW ALSO ENFORCES REVOCATION AND TOKEN TYPE.

    Previously it checked the signature and the expiry and nothing else, which meant:
      - a revoked token still worked (there was no revocation at all)
      - a stolen REFRESH token could be presented as an ACCESS token, buying the
        attacker seven days of API access instead of fifteen minutes

    Both are now closed. See decode_token() below, which this delegates to.
    """
    return decode_token(token, expected_type="access")


# ===========================================================================
# REFRESH TOKENS AND REVOCATION
# ===========================================================================
#
# The original design issued a single 30-minute access token and nothing else. Two
# consequences, and both are the kind of thing a security reviewer opens with:
#
#   1. NO LOGOUT. A JWT is self-validating - the server checks the signature and
#      the expiry and asks nobody's permission. So "log out" meant "delete the
#      token from your own browser", and a stolen token stayed valid for its full
#      30 minutes no matter what anyone did. There was no way to revoke it. On a
#      product that surveils employees, that is not acceptable.
#
#   2. NO SESSION. Thirty minutes, then re-enter your password. An analyst working
#      an incident re-authenticates every half hour. In practice people respond to
#      that by choosing weaker passwords, which makes the system less secure, not
#      more.
#
# The fix is the standard OAuth2 pattern, and it is standard because it works:
#
#   - a SHORT-LIVED access token (15 min) that is used on every request
#   - a LONG-LIVED refresh token (7 days) whose ONLY power is to mint a new access
#     token, and which can be revoked
#
# The blast radius of a stolen access token is now 15 minutes. The refresh token is
# sent rarely, stored more carefully, and - critically - can be killed.

REVOKED_TOKENS: set[str] = set()
"""In-memory revocation list, keyed by the token's `jti` claim.

BE HONEST ABOUT WHAT THIS IS. It is a Python set in one process. It does not
survive a restart, and it does not work across multiple workers - two uvicorn
processes have two different sets, and a token revoked on one is still accepted by
the other.

That is a REAL limitation and it is written down here rather than hidden. The
correct production answer is Redis with a TTL matching the token's own expiry, so
the entry evicts itself exactly when it stops mattering. That is a genuine
dependency, and adding a whole datastore for one feature is not obviously right at
this stage - so the tradeoff is made deliberately, and stated, rather than made
accidentally and discovered later.
"""


def create_refresh_token(subject: str) -> tuple[str, str]:
    """Mint a refresh token. Returns (token, jti).

    The `jti` (JWT ID) is what makes revocation possible at all: it gives the token
    an identity, so we can name it in a blacklist. A JWT without a jti cannot be
    revoked - you can only wait for it to expire.
    """
    settings = get_settings()
    jti = str(uuid.uuid4())
    now = datetime.now(UTC)

    payload = {
        "sub": subject,
        "jti": jti,
        # The token TYPE is inside the signed payload, not just in how we use it.
        #
        # Without this, an attacker who steals a refresh token can present it as an
        # access token and get 7 days of API access instead of a 15-minute window.
        # The two tokens are signed with the same key and are structurally
        # identical, so nothing else distinguishes them. This claim is checked on
        # every request - see decode_token(expected_type=...).
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, jti


def decode_token(token: str, expected_type: str = "access") -> dict[str, Any] | None:
    """Decode and validate a token, enforcing its TYPE.

    `expected_type` is the whole point. An access token and a refresh token are both
    JWTs signed with the same key - they are indistinguishable unless you look at
    the type claim. Skip this check and a stolen refresh token becomes a 7-day API
    key.
    """
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError:
        return None

    if payload.get("type") != expected_type:
        return None

    jti = payload.get("jti")
    if jti and jti in REVOKED_TOKENS:
        return None

    return payload


def revoke_token(token: str) -> bool:
    """Revoke a token by its jti. This is what makes /logout mean something."""
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_exp": False},  # an expired token can still be revoked
        )
    except JWTError:
        return False

    jti = payload.get("jti")
    if not jti:
        return False

    REVOKED_TOKENS.add(jti)
    return True


# ===========================================================================
# BRUTE-FORCE PROTECTION
# ===========================================================================

MAX_FAILED_LOGINS = 5
LOCKOUT_MINUTES = 15


def is_locked_out(user: Any) -> bool:
    """Is this account currently locked?

    Without a lockout, /login is an unlimited password-guessing oracle. An attacker
    with a wordlist gets in over a weekend, and nothing looks unusual in the logs -
    every individual request is an entirely ordinary failed login.

    Five attempts, then fifteen minutes in the corner. That turns an 8-character
    password from hours of guessing into centuries, and it costs a legitimate user -
    who has mistyped their password five times - a quarter of an hour.
    """
    if user.locked_until is None:
        return False
    return datetime.now(UTC) < user.locked_until


def register_failed_login(user: Any) -> None:
    """Count a failure, and lock the account if there have been too many."""
    user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
    if user.failed_login_attempts >= MAX_FAILED_LOGINS:
        user.locked_until = datetime.now(UTC) + timedelta(
            minutes=LOCKOUT_MINUTES
        )


def register_successful_login(user: Any) -> None:
    """Clear the failure counter. A success wipes the slate."""
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = datetime.now(UTC)


# ===========================================================================
# PASSWORD POLICY
# ===========================================================================

MIN_PASSWORD_LENGTH = 12


def password_problems(password: str) -> list[str]:
    """Return every reason this password is unacceptable. Empty list = fine.

    Twelve characters, not eight. Eight is a 1990s number - it predates GPUs, and a
    modern rig guesses every 8-character password in hours. Twelve with mixed
    classes is still out of reach.

    The rules are deliberately boring and deliberately EXPLAINED to the user. A
    policy that says only "password too weak" trains people to append "1!" until it
    shuts up, which produces exactly the passwords the policy was meant to prevent.
    """
    problems: list[str] = []

    if len(password) < MIN_PASSWORD_LENGTH:
        problems.append(
            f"must be at least {MIN_PASSWORD_LENGTH} characters "
            f"(this one is {len(password)})"
        )
    if not any(c.islower() for c in password):
        problems.append("must contain a lowercase letter")
    if not any(c.isupper() for c in password):
        problems.append("must contain an uppercase letter")
    if not any(c.isdigit() for c in password):
        problems.append("must contain a digit")
    if not any(not c.isalnum() for c in password):
        problems.append("must contain a symbol")

    # The passwords that actually get used. A length rule does not stop
    # "Password1234!" - it satisfies every complexity requirement above and is in
    # every wordlist on earth.
    common = {
        "password", "passw0rd", "qwerty", "letmein", "welcome",
        "admin", "administrator", "changeme", "insider", "threat",
        "security", "monkey", "dragon", "iloveyou", "sunshine",
    }
    lowered = password.lower()
    if any(c in lowered for c in common):
        problems.append("contains a common word that appears in every wordlist")

    return problems