from dataclasses import dataclass              # simple, typed container for user data
from passlib.context import CryptContext       # provides bcrypt hashing/verification


pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


@dataclass
class User:
    id: int
    email: str
    hashed_password: str
    is_active: bool = True


# In-memory user list for demo (replace with DB later)
# Password for this demo user is: "password123"
_USERS: list[User] = [
    User(
        id=1,
        email="demo@example.com",
        hashed_password=pwd_context.hash("password123"),  # store only hashes
        is_active=True,
    )
]


def get_user_by_email(email: str) -> User | None:
    """Return the User object matching the given email, or None."""
    for user in _USERS:
        if user.email == email:
            return user
    return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compare plain pasword with stored bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_user_by_id(user_id: int) -> User | None:
    """Return the User object with this id, or None if not found."""
    for user in _USERS:
        if user.id == user_id:
            return user
    return None
