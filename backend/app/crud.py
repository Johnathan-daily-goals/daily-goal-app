from psycopg2.extras import RealDictCursor
from psycopg2 import errors as pg_errors
from backend.app.errors import DailyGoalAlreadyExists


def create_project(conn, name: str, description: str = None) -> int:
    """Insert a new project and return its ID."""
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO projects (name, description)
        VALUES (%s, %s)
        RETURNING id;
        """,
        (name, description)
    )
    project_id = cur.fetchone()["id"]
    cur.close()
    return project_id


def get_projects(conn):
    """Return all projects."""
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "SELECT id, name, description, created_at FROM projects;"
    )
    projects = cur.fetchall()
    cur.close()
    return projects


def create_daily_goal(conn, project_id: int, goal_text: str) -> int:
    """Insert a new daily goal and return its ID."""
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO daily_goals (project_id, goal_text)
            VALUES (%s, %s)
            RETURNING id;
            """,
            (project_id, goal_text),
        )
        return cur.fetchone()["id"]

    except pg_errors.UniqueViolation as e:
        raise DailyGoalAlreadyExists() from e

    finally:
        cur.close()

def get_daily_goals(conn, project_id: int):
    """Return all daily goals for a given project."""
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        """
        SELECT id, goal_text, created_at
        FROM daily_goals
        WHERE project_id = %s;
        """,
        (project_id,)
    )
    goals = cur.fetchall()
    cur.close()
    return goals