from flask import request
from backend.app.errors import Unauthorized
from psycopg2.extras import RealDictCursor


def get_user_from_request(conn):
    """
    Reads token from 'Authorization: Bearer <token>' or 'X-API-Token: <token>'.
    Returns user dict if valid, otherwise raises Unauthorized.
    """
    auth_header = request.headers.get("Authorization", "")
    token = None

    if auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "", 1).strip()

    if not token:
        token = request.headers.get("X-API-Token")

    if not token:
        raise Unauthorized("Missing auth token")

    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, email, token FROM users WHERE token = %s;", (token,))
    user = cur.fetchone()
    cur.close()

    if not user:
        raise Unauthorized("Invalid auth token")

    return user
