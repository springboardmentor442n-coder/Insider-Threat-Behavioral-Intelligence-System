"""Rate limiting.

WHY THIS EXISTS - AND WHY THE ACCOUNT LOCKOUT IS NOT ENOUGH ON ITS OWN
----------------------------------------------------------------------
The account lockout (5 failures, 15 minutes) stops an attacker guessing ONE
account's password. It does nothing at all about the attack that actually works
against organisations: PASSWORD SPRAYING.

Instead of trying a thousand passwords against one account - which trips the lock -
the attacker tries ONE password ("Autumn2025!") against a thousand accounts. Every
account sees a single failed login. No lockout ever fires. Nothing looks unusual.
And in an organisation of any size, someone is using that password.

Lockout is per-ACCOUNT. Rate limiting is per-IP. You need both, because they defend
against different attacks, and neither substitutes for the other.

WHAT IS LIMITED, AND WHY THOSE NUMBERS
--------------------------------------
  /login           10/minute   A human needs three or four. Ten is generous.
                               A sprayer needs thousands.
  /register         5/hour     Nobody legitimately creates six operator accounts
                               an hour. An attacker seeding backdoor accounts does.
  /refresh         30/minute   Called automatically, so the ceiling is higher -
                               but a stolen refresh token being farmed for access
                               tokens should still hit a wall.

THE HONEST LIMITATION
---------------------
The counters live in memory, in one process. Two uvicorn workers have two separate
sets of counters, so the real limit is (workers x limit). And an attacker with a
botnet has many IPs, so per-IP limiting slows them rather than stopping them.

The production answer is a shared Redis backend and limiting at the edge (an API
gateway or CDN) rather than in the application. That is a real dependency and a real
architectural decision, so it is written down here rather than quietly assumed.

What this DOES do, today, is turn "spray a thousand accounts in a minute" into
"spray a thousand accounts over two hours" - which is long enough for the audit log
to be worth reading, and that is the whole point of having one.
"""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

from backend.app.config import get_settings

limiter = Limiter(
    key_func=get_remote_address,
    enabled=get_settings().RATE_LIMIT_ENABLED,
    # Applied to every endpoint that does not set its own. Deliberately loose: this
    # is a backstop against a runaway client, not a security control. The security
    # controls are the explicit per-endpoint limits on the auth routes.
    default_limits=["300/minute"],
)