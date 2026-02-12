# backend/test_db.py
from db import Database

db = Database()
conn = db.connect()
cur = conn.cursor()

# Create a project if none exist
cur.execute("SELECT * FROM projects;")
projects = cur.fetchall()
if not projects:
    cur.execute(
        "INSERT INTO projects (name) VALUES (%s) RETURNING id;",
        ("Test Project",)
    )
    project_id = cur.fetchone()['id']
    print("Created project with ID:", project_id)
else:
    project_id = projects[0]['id']
    print("Using existing project with ID:", project_id)

# Insert a new daily goal
cur.execute(
    "INSERT INTO daily_goals (project_id, goal_text, date_created) VALUES (%s, %s, NOW()) RETURNING id;",
    (project_id, "Test daily goal")
)
new_goal_id = cur.fetchone()['id']
print("Inserted daily goal with ID:", new_goal_id)

conn.commit()
cur.close()
db.close()