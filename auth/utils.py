
def require_login(info):
    """Raise if user not logged in, else return the user."""
    user = info.context.user
    if user is None:
        raise Exception("Please log in.")
    return user
