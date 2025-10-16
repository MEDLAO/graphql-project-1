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
    return sid  # caller (login route) will set this value in an HttpOnly cookie


def get_user_id(session_id: Optional[str]) -> Optional[int]:
    """Return the user_id if the session is valid and not expired."""
    if not session_id:                    # no cookie sent
        return None

    data = _SESSIONS.get(session_id)      # find this session
    if not data:                          # unknown id
        return None

    if data["expires_at"] < _now():       # expired session
        _SESSIONS.pop(session_id, None)   # remove it
        return None

    return int(data["user_id"])           # valid -> return linked user


def delete_session(session_id: Optional[str]) -> None:
    """Invalidate a session (used on logout)."""
    if session_id:                       # if a cookie value was sent
        _SESSIONS.pop(session_id, None)  # remove it from the in-memory store (no error if missing)

