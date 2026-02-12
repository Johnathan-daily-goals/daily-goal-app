from psycopg2.extras import RealDictCursor
from psycopg2 import errors as pg_errors
from backend.app.errors import DailyGoalAlreadyExists, ProjectNotFound


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
        ON CONFLICT (project_id, (date(created_at)))
        DO UPDATE SET goal_text = EXCLUDED.goal_text
        RETURNING id, project_id, user_id, goal_text, created_at, (xmax = 0) AS inserted;
        """,
        (project_id, user_id, goal_text),
    )
    row = cur.fetchone()
    cur.close()
    return row