from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel
from strawberry.fastapi import GraphQLRouter
from app_graphql.schema import schema
from auth.users import get_user_by_email, verify_password, get_user_by_id
from auth.sessions import create_session, delete_session, get_user_id
from config import COOKIE_NAME, COOKIE_PATH, COOKIE_SAMESITE, COOKIE_SECURE, COOKIE_HTTPONLY
from auth.utils import require_login


app = FastAPI()


# This runs once per GraphQL request to build a tiny "context" object
async def get_context(request: Request, response: Response):
    # 1 - try to read the 'session_id' cookie sent by the browser
    session_id = request.cookies.get(COOKIE_NAME)

    # 2 - find which user owns this session (if any)
    user_id = get_user_id(session_id)

    # 3 - load the actual User object when we have a valid user_id, else stay anonymous
    user = get_user_by_id(user_id) if user_id else None

    # 4 - return a small dict that resolvers can read via info.context
    return {
        "request": request,
        "response": response,
        "user": user,
        "session_id": session_id,
        "user_id": user_id,
    }


# Turn the schema into a GraphQL route
graphql_app = GraphQLRouter(schema,  context_getter=get_context)

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

    # 4 - store session_id in a cookie so the browser sends it automatically later
    response.set_cookie(
        key=COOKIE_NAME,
        value=session_id,
        httponly=COOKIE_HTTPONLY,
        samesite=COOKIE_SAMESITE,
        secure=COOKIE_SECURE,
        path=COOKIE_PATH,
    )

    # 5 - small JSON response for the client
    return {"ok": True}


@app.post("/logout")
async def logout(request: Request, response: Response):
    """Logout current user: remove session and clear cookie."""
    # 1 - Read the cookie from the incoming request
    session_id = request.cookies.get(COOKIE_NAME)

    # 2 - Delete the session from the server-side store (if it exists)
    delete_session(session_id)

    # 3 - Instruct browser to remove its cookie
    response.delete_cookie(
        key=COOKIE_NAME,
        path=COOKIE_PATH,
        samesite=COOKIE_SAMESITE,
        secure=COOKIE_SECURE,
    )

    # 4 - Return confirmation
    return {"ok": True}
