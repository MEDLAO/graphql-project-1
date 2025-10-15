import uuid                               # generate random session ids
from datetime import datetime, timedelta  # handle expiry times
from typing import Optional               # type hint for optional values


# how long a session should live (in minutes)
SESSION_TTL_MINUTES = 120

# in-memory map: session_id -> {"user_id": int, "expires_at": datetime}
_SESSIONS: dict[str, dict] = {}


def _now() -> datetime:
    """Return current UTC time (small helper)."""
    return datetime.utcnow()


def create_session(user_id: int) -> str:
    """Create a new session for a user and return its opaque id."""
    sid = uuid.uuid4().hex  # random, opaque session id (no user info inside)
    _SESSIONS[sid] = {
        "user_id": user_id,  # who owns this session
        "expires_at": _now() + timedelta(minutes=SESSION_TTL_MINUTES),  # expiry timestamp (UTC)
    }
    return sid

