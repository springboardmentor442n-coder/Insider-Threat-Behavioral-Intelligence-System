"""Pydantic schemas: the API's contract with the outside world.

Models (models.py) are what the DATABASE stores.
Schemas (this file) are what the API accepts and returns.

Keeping them separate is not ceremony - it is what stops `hashed_password` from
ever appearing in a JSON response. The ORM model has that column; the response
schema simply does not declare it, so it cannot leak. If we returned ORM objects
directly, every new column would be exposed by default. Here, exposure is
opt-in.
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from backend.app.models import AlertSeverity, AlertStatus, UserRole
from backend.app.security import MAX_PASSWORD_BYTES

# ===========================================================================
# Authentication
# ===========================================================================


class UserRegister(BaseModel):
    """Payload for creating a new platform operator."""

    email: EmailStr  # EmailStr rejects malformed addresses before we touch the DB
    full_name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=72)
    role: UserRole = UserRole.SECURITY_ANALYST  # least privilege by default

    @field_validator("password")
    @classmethod
    def password_within_bcrypt_limit(cls, v: str) -> str:
        """Reject passwords bcrypt physically cannot hash.

        max_length=8..72 above counts CHARACTERS. bcrypt's limit is 72 BYTES.
        A password of 72 accented or CJK characters passes the character check
        and then explodes in the hasher, because those characters are 2-4 bytes
        each in UTF-8. Checking the encoded length is the only correct check.
        """
        if len(v.encode("utf-8")) > MAX_PASSWORD_BYTES:
            raise ValueError(
                f"Password must be at most {MAX_PASSWORD_BYTES} bytes when "
                "UTF-8 encoded (non-ASCII characters use more than one byte)."
            )
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    """What a successful login returns.

    `bearer` is the OAuth2 token type; clients send it back as
    `Authorization: Bearer <token>`.
    """

    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds - lets the client refresh before expiry

    # The refresh token. Optional, because /refresh returns the caller's existing
    # one rather than rotating it, and a future OAuth2 client-credentials flow would
    # not issue one at all.
    #
    # This is what carries the SESSION. The access token now lives fifteen minutes -
    # short, because it is sent on every request and is therefore the token most
    # likely to leak. The refresh token lives seven days, is sent rarely, and can be
    # REVOKED, which is what makes /logout mean something.
    refresh_token: str | None = None


class UserResponse(BaseModel):
    """A platform operator, as returned by the API.

    Note what is absent: hashed_password. It exists on the ORM model and it is
    simply not declared here, so it can never be serialised into a response.
    """

    model_config = ConfigDict(from_attributes=True)  # allows ORM -> schema

    id: int
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login_at: datetime | None = None


# ===========================================================================
# Monitored employees
# ===========================================================================


class EmployeeResponse(BaseModel):
    """A monitored employee from the CERT dataset."""

    model_config = ConfigDict(from_attributes=True)

    user_id: str
    employee_name: str
    email: str | None = None
    role: str | None = None
    department: str | None = None
    team: str | None = None
    supervisor: str | None = None


class EmployeeDetailResponse(EmployeeResponse):
    """Employee detail, including ground-truth labels.

    Ground truth is exposed ONLY on this detail endpoint, and only to
    Security Managers and Administrators. An analyst who could see
    `is_insider` would not be investigating - they would be reading the answer
    key, which defeats the purpose of the exercise and of the tool.
    """

    is_insider: bool
    insider_scenario: int | None = None


class IngestionStats(BaseModel):
    """What an ingestion run loaded. Returned by the ingest CLI and endpoint."""

    employees: int = 0
    logon_events: int = 0
    device_events: int = 0
    file_events: int = 0
    email_events: int = 0
    http_daily_rows: int = 0
    ground_truth_rows: int = 0

    # The SECOND answer key: the days attacks ACTUALLY happened, from CERT's
    # per-insider files. insiders.csv gives a WINDOW; these give the events.
    # They disagree about 49% of the malicious days.
    malicious_event_days: int = 0
    duration_seconds: float = 0.0


class RefreshRequest(BaseModel):
    """Body for POST /api/auth/refresh."""

    refresh_token: str


class LogoutRequest(BaseModel):
    """Body for POST /api/auth/logout.

    The refresh token is optional: a caller may only be holding an access token.
    The access token is taken from the Authorization header, so it is always
    revoked regardless.
    """

    refresh_token: str | None = None


class PasswordChangeRequest(BaseModel):
    """Body for POST /api/auth/change-password.

    `current_password` is required and is not a formality: without it, anyone
    holding a stolen access token could change the victim's password and lock them
    out of their own account - turning a fifteen-minute token theft into a permanent
    account takeover.
    """

    current_password: str
    new_password: str


class UserSelfUpdate(BaseModel):
    """PATCH /api/users/me - what a user may change about THEMSELVES.

    NOTE WHAT IS ABSENT: `role`.

    That omission is the security control. If this schema had a role field, the
    lowest-privileged account on the platform could promote itself to Administrator
    in one request, and every RBAC check in the codebase would become theatre.

    The defence against privilege escalation through a profile endpoint is not to
    validate the field carefully. It is to NOT HAVE THE FIELD. A field that does not
    exist cannot be forgotten about, mis-validated, or re-introduced by someone who
    did not know why it was missing.

    `password` is absent for the same reason: changing it goes through
    /api/auth/change-password, which demands the CURRENT password. Allowing it here -
    authenticated by a bearer token alone - would turn a stolen fifteen-minute
    access token into a permanent account takeover.
    """

    full_name: str | None = None
    email: EmailStr | None = None


class UserAdminUpdate(BaseModel):
    """PATCH /api/users/{id} - what an ADMINISTRATOR may change about someone else.

    This one DOES carry `role`, because changing roles is the entire point of having
    an administrator. The guards live in the endpoint: you cannot change your own
    role, you cannot deactivate yourself, and you cannot remove the last remaining
    administrator.
    """

    full_name: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None

    # Clear a brute-force lockout. Five typos should not cost fifteen minutes if an
    # administrator is sitting right there.
    unlock: bool = False


# ===========================================================================
# ALERTS  (spec Module 9)
# ===========================================================================


class AlertNoteCreate(BaseModel):
    body: str = Field(min_length=1, max_length=4000)


class AlertNoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    alert_id: int
    author_id: int
    body: str
    created_at: datetime


class AlertAssign(BaseModel):
    """Null un-assigns, returning the alert to the pool."""

    assignee_id: int | None = None


class AlertResolve(BaseModel):
    """Closing an alert.

    `true_positive` is REQUIRED, and there is no default.

    A default would be a lie dressed as a convenience: whichever way it defaulted,
    half the verdicts in the system would be a value nobody chose. And these verdicts
    are the only ground truth that exists in production - they are how precision gets
    measured on live traffic, and they are the training signal for the next model.
    Guessing them is worse than not collecting them.
    """

    true_positive: bool
    note: str | None = Field(default=None, max_length=4000)


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: str
    alert_date: date
    severity: AlertSeverity
    status: AlertStatus
    risk_score: float
    ml_probability: float
    assigned_to_id: int | None
    created_at: datetime


class AlertDetailResponse(AlertResponse):
    """The full alert - the evidence, not just the verdict.

    `components` is WHICH of the five risk categories drove the score.
    `top_features` is WHICH specific behaviours, with numbers and direction -
    including what argued AGAINST the alert, which is what lets an analyst close a
    false positive in five seconds instead of an hour.
    """

    components: dict = {}
    top_features: list = []
    acknowledged_at: datetime | None = None
    resolved_at: datetime | None = None
    resolution_note: str | None = None
    notes: list[AlertNoteResponse] = []


class AlertSummaryResponse(BaseModel):
    total: int
    open: int
    unassigned_open: int
    by_severity: dict[str, int]
    by_status: dict[str, int]