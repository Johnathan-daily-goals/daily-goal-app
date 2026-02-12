import uuid
from psycopg2.extras import RealDictCursor
from psycopg2 import errors as pg_errors
from backend.app.errors import DailyGoalAlreadyExists, ProjectNotFound
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
import secrets

def get_user_by_token(conn, token: str):
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "SELECT id, email FROM users WHERE token = %s;",
        (token,),
    )
    row = cur.fetchone()
    cur.close()
    return row


def create_project(conn, user_id: int, name: str, description: str = None) -> int:
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO projects (user_id, name, description)
        VALUES (%s, %s, %s)
        RETURNING id;
        """,
        (user_id, name, description),
    )
    new_id = cur.fetchone()["id"]
    cur.close()
    return new_id


def get_projects(conn, user_id: int):
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        """
        SELECT id, name, description, created_at
        FROM projects
        WHERE user_id = %s AND archived_at IS NULL
        ORDER BY id;
        """,
        (user_id,),
    )
    rows = cur.fetchall()
    cur.close()
    return rows


def get_project(conn, project_id: int, user_id: int):
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        """
        SELECT id, name, description, created_at, archived_at
        FROM projects
        WHERE id = %s AND user_id = %s;
        """,
        (project_id, user_id),
    )
    project = cur.fetchone()
    cur.close()
    return project


def project_exists(conn, project_id: int, user_id: int) -> bool:
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM projects WHERE id = %s AND user_id = %s;",
        (project_id, user_id),
    )
    exists = cur.fetchone() is not None
    cur.close()
    return exists


def archive_project(conn, project_id: int, user_id: int) -> bool:
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE projects
        SET archived_at = CURRENT_TIMESTAMP
        WHERE id = %s AND user_id = %s AND archived_at IS NULL
        RETURNING id;
        """,
        (project_id, user_id),
    )
    updated = cur.fetchone() is not None
    cur.close()
    return updated


def get_archived_projects(conn, user_id: int):
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        """
        SELECT id, name, description, created_at, archived_at
        FROM projects
        WHERE user_id = %s AND archived_at IS NOT NULL
        ORDER BY archived_at DESC, id DESC;
        """,
        (user_id,),
    )
    rows = cur.fetchall()
    cur.close()
    return rows


def restore_project(conn, project_id: int, user_id: int) -> bool:
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE projects
        SET archived_at = NULL
        WHERE id = %s AND user_id = %s AND archived_at IS NOT NULL
        RETURNING id;
        """,
        (project_id, user_id),
    )
    updated = cur.fetchone() is not None
    cur.close()
    return updated


def create_daily_goal(conn, project_id: int, user_id: int, goal_text: str) -> int:
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO daily_goals (project_id, user_id, goal_text)
            VALUES (%s, %s, %s)
            RETURNING id;
            """,
            (project_id, user_id, goal_text),
        )
        return cur.fetchone()["id"]

    except pg_errors.UniqueViolation as e:
        raise DailyGoalAlreadyExists() from e

    except pg_errors.ForeignKeyViolation as e:
        raise ProjectNotFound() from e

    finally:
        cur.close()


def get_daily_goals(conn, project_id: int, user_id: int):
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        """
        SELECT id, goal_text, created_at
        FROM daily_goals
        WHERE project_id = %s AND user_id = %s
        ORDER BY created_at DESC, id DESC;
        """,
        (project_id, user_id),
    )
    goals = cur.fetchall()
    cur.close()
    return goals


def get_todays_goal(conn, project_id: int, user_id: int):
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        """
        SELECT id, project_id, goal_text, created_at
        FROM daily_goals
        WHERE project_id = %s
          AND user_id = %s
          AND DATE(created_at) = CURRENT_DATE
        ORDER BY created_at DESC
        LIMIT 1;
        """,
        (project_id, user_id),
    )
    goal = cur.fetchone()
    cur.close()
    return goal


def upsert_daily_goal_today(conn, project_id: int, user_id: int, goal_text: str) -> dict:
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        """
        INSERT INTO daily_goals (project_id, user_id, goal_text)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id, project_id, (date(created_at)))
        DO UPDATE SET goal_text = EXCLUDED.goal_text
        RETURNING id, project_id, user_id, goal_text, created_at, (xmax = 0) AS inserted;
        """,
        (project_id, user_id, goal_text),
    )
    row = cur.fetchone()
    cur.close()
    return row

def get_user_by_email(conn, email: str):
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "SELECT id, email, password_hash, token FROM users WHERE email = %s;",
        (email,),
    )
    row = cur.fetchone()
    cur.close()
    return row


def create_user(conn, email: str, password: str) -> dict:
    password_hash = generate_password_hash(password)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        """
        INSERT INTO users (email, password_hash, token)
        VALUES (%s, %s, gen_random_uuid()::text)
        RETURNING id, email, token;
        """,
        (email, password_hash),
    )
    row = cur.fetchone()
    cur.close()
    return row


def verify_user_password(conn, email: str, password: str) -> dict | None:
    user = get_user_by_email(conn, email)
    if not user:
        return None
    if not user["password_hash"]:
        return None
    if not check_password_hash(user["password_hash"], password):
        return None
    return user


def rotate_user_token(conn, user_id: int) -> str:
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        """
        UPDATE users
        SET token = gen_random_uuid()::text
        WHERE id = %s
        RETURNING token;
        """,
        (user_id,),
    )
    row = cur.fetchone()
    cur.close()
    return row["token"]

def rotate_user_token(conn, user_id: int) -> str:
    cur = conn.cursor(cursor_factory=RealDictCursor)
    new_token = str(uuid.uuid4())
    cur.execute(
        "UPDATE users SET token = %s WHERE id = %s RETURNING token;",
        (new_token, user_id),
    )
    row = cur.fetchone()
    cur.close()
    return row["token"]

def revoke_refresh_token(conn, user_id: int, token: str) -> bool:
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE refresh_tokens
        SET revoked_at = CURRENT_TIMESTAMP
        WHERE token = %s
          AND user_id = %s
          AND revoked_at IS NULL
        RETURNING id;
        """,
        (token, user_id),
    )
    revoked = cur.fetchone() is not None
    cur.close()
    return revoked

def create_refresh_token(conn, user_id: int, ttl_seconds: int = 60 * 60 * 24 * 30) -> dict:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(seconds=ttl_seconds)

    token = secrets.token_urlsafe(32)

    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        """
        INSERT INTO refresh_tokens (user_id, token, expires_at)
        VALUES (%s, %s, %s)
        RETURNING id, user_id, token, created_at, expires_at, revoked_at;
        """,
        (user_id, token, expires_at),
    )
    row = cur.fetchone()
    cur.close()
    return row


def get_valid_refresh_token(conn, token: str) -> dict | None:
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        """
        SELECT id, user_id, token, created_at, expires_at, revoked_at
        FROM refresh_tokens
        WHERE token = %s
          AND revoked_at IS NULL
          AND expires_at > CURRENT_TIMESTAMP;
        """,
        (token,),
    )
    row = cur.fetchone()
    cur.close()
    return row