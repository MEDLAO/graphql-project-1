from dataclasses import dataclass              # simple, typed container for user data
from passlib.context import CryptContext       # provides bcrypt hashing/verification


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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

