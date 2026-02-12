from psycopg2.extras import RealDictCursor
from psycopg2 import errors as pg_errors
from backend.app.errors import DailyGoalAlreadyExists, ProjectNotFound


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
    "SELECT id, name, description, created_at FROM projects WHERE archived_at IS NULL ORDER BY id;"
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
            (project_id, goal_text)
        )
        return cur.fetchone()["id"]

    except pg_errors.UniqueViolation as e:
        # unique constraint violation means there's already a daily goal for this project today
        raise DailyGoalAlreadyExists() from e

    except pg_errors.ForeignKeyViolation as e:
        # project_id doesn't exist in projects(id)
        raise ProjectNotFound() from e

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

def get_project(conn, project_id: int):
    """Return a single project dict, or None if not found."""
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        """
        SELECT id, name, description, created_at, archived_at
        FROM projects
        WHERE id = %s;
        """,
        (project_id,),
    )
    project = cur.fetchone()
    cur.close()
    return project

def project_exists(conn, project_id: int) -> bool:
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM projects WHERE id = %s;", (project_id,))
    exists = cur.fetchone() is not None
    cur.close()
    return exists

def archive_project(conn, project_id: int) -> bool:
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE projects
        SET archived_at = CURRENT_TIMESTAMP
        WHERE id = %s AND archived_at IS NULL
        RETURNING id;
        """,
        (project_id,),
    )
    updated = cur.fetchone() is not None
    cur.close()
    return updated

def get_archived_projects(conn):
    """Return archived projects only."""
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        """
        SELECT id, name, description, created_at, archived_at
        FROM projects
        WHERE archived_at IS NOT NULL
        ORDER BY archived_at DESC, id DESC;
        """
    )
    projects = cur.fetchall()
    cur.close()
    return projects

def restore_project(conn, project_id: int) -> bool:
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE projects
        SET archived_at = NULL
        WHERE id = %s AND archived_at IS NOT NULL
        RETURNING id;
        """,
        (project_id,),
    )
    updated = cur.fetchone() is not None
    cur.close()
    return updated

def get_todays_goal(conn, project_id: int):
    """Return today's goal for a project, or None if not set."""
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        """
        SELECT id, project_id, goal_text, created_at
        FROM daily_goals
        WHERE project_id = %s
          AND DATE(created_at) = CURRENT_DATE
        ORDER BY created_at DESC
        LIMIT 1;
        """,
        (project_id,),
    )
    goal = cur.fetchone()
    cur.close()
    return goal