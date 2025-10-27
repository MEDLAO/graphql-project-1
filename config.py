# -------- Cookie settings (simple defaults for dev) --------
COOKIE_NAME = "session_id"
COOKIE_PATH = "/"
COOKIE_SAMESITE = "lax"       # good default to reduce CSRF risk
COOKIE_SECURE = False         # set True in production (HTTPS only)
COOKIE_HTTPONLY = True        # hides cookie from JS (XSS protection)
