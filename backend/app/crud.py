def create_project(conn, name: str) -> int:
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO projects (name) VALUES (%s) RETURNING id;",
        (name,)
    )

    project_id = cur.fetchone()["id"]
    cur.close()

    return project_id


def get_projects(conn):
    cur = conn.cursor()

    cur.execute(
        "SELECT id, name, date_created FROM projects;"
    )

    projects = cur.fetchall()
    cur.close()

    return projects


def create_daily_goal(conn, project_id: int, goal_text: str) -> int:
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO daily_goals (project_id, goal_text)
        VALUES (%s, %s)
        RETURNING id;
        """,
        (project_id, goal_text)
    )

    goal_id = cur.fetchone()["id"]
    cur.close()

    return goal_id


def get_daily_goals(conn, project_id: int):
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, goal_text, date_created
        FROM daily_goals
        WHERE project_id = %s;
        """,
        (project_id,)
    )

    goals = cur.fetchall()
    cur.close()

    return goals