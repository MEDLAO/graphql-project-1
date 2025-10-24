

def require_login(info):
    """Ensure the user is authenticated before running a mutation."""
    # 1 - get user from the context (dict from get_context)
    user = info.context.get("user")

    # 2 - if no user, raise an auth error
    if not user:
        raise Exception("Login required")

    # 3 - otherwise, return the user (optional, can be used by resolvers)
    return user
