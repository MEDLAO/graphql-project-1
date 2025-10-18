from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from strawberry.fastapi import GraphQLRouter
from graphql.schema import schema
from auth.users import get_user_by_email, verify_password
from auth.sessions import create_session


app = FastAPI()


# ----- Cookie settings (simple default dev) -----
COOKIE_NAME = "session_id"  # the cookie key the browser will store
COOKIE_PATH = "/"           # valid for the whole site
COOKIE_SAMESITE = "lax"     # good default to reduce CSRF risk
COOKIE_SECURE = False       # set True in production (HTTPS only)
COOKIE_HTTPONLY = True      # hides cookie from JS (XSS protection)

# Turn the schema into a GraphQL route
graphql_app = GraphQLRouter(schema)

# Mount the GraphQL route at /graphql
app.include_router(graphql_app, prefix="/graphql")


# Request model for login (JSON body)
class LoginInput(BaseModel):
    email: str
    password: str


# /login route: verifies creds, sets session cookie
@app.post("/login")
async def login(payload: LoginInput, response: Response):
    # 1 - look up the user by email
    user = get_user_by_email(payload.email)

    # 2 - check user exists, is active and password matches
    if not user or not user.is_active or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")  # generic error (no leaks)

    # 3 - create a server-side session and get an opaque session_id
    session_id = create_session(user.id)

