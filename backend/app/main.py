from flask import Flask, request, jsonify, g
from backend.app.database import Database
from backend.app import crud
from backend.app.errors import AppError, Unauthorized, BadRequest
from datetime import datetime, timezone
from uuid import uuid4


app = Flask(__name__)
database = Database()


def to_iso(dt):
    if dt is None:
        return None
    if isinstance(dt, str):
        return dt
    if isinstance(dt, datetime):
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat().replace("+00:00", "Z")
    return str(dt)


@app.before_request
def open_db_connection():
    g.db_conn = database.get_connection()


@app.before_request
def authenticate_request():
    if request.path in ("/health", "/auth/register", "/auth/login"):
        return

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise Unauthorized("Missing or invalid Authorization header")

    token = auth_header.removeprefix("Bearer ").strip()
    if not token:
        raise Unauthorized("Missing or invalid Authorization header")

    user = crud.get_user_by_token(g.db_conn, token)
    if not user:
        raise Unauthorized("Invalid token")

    g.user_id = user["id"]


@app.teardown_request
def close_db_connection(exception=None):
    conn = getattr(g, "db_conn", None)
    if conn:
        if exception:
            conn.rollback()
        else:
            conn.commit()
        conn.close()


@app.errorhandler(AppError)
def handle_app_error(err: AppError):
    return jsonify({"error": err.detail}), err.status_code


@app.route("/projects", methods=["POST"])
def create_project():
    data = request.get_json()
    name = data.get("name")
    description = data.get("description")

    if not name:
        return jsonify({"error": "Project name required"}), 400

    project_id = crud.create_project(g.db_conn, g.user_id, name, description)

    return jsonify({
        "id": project_id,
        "name": name,
        "description": description
    }), 201


@app.route("/projects", methods=["GET"])
def get_projects():
    projects = crud.get_projects(g.db_conn, g.user_id)
    return jsonify(projects), 200


@app.route("/projects/<int:project_id>/goals", methods=["POST"])
def create_daily_goal(project_id):
    project = crud.get_project(g.db_conn, project_id, g.user_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    data = request.get_json()
    goal_text = data.get("goal_text")

    if not goal_text:
        return jsonify({"error": "goal_text required"}), 400

    goal_id = crud.create_daily_goal(g.db_conn, project_id, g.user_id, goal_text)

    return jsonify({
        "id": goal_id,
        "project_id": project_id,
        "goal_text": goal_text
    }), 201


@app.route("/projects/<int:project_id>/goals", methods=["GET"])
def get_daily_goals(project_id):
    if not crud.project_exists(g.db_conn, project_id, g.user_id):
        return jsonify({"error": "Project not found"}), 404

    goals = crud.get_daily_goals(g.db_conn, project_id, g.user_id)
    return jsonify(goals), 200


@app.route("/projects/<int:project_id>/archive", methods=["POST"])
def archive_project(project_id):
    if not crud.project_exists(g.db_conn, project_id, g.user_id):
        return jsonify({"error": "Project not found"}), 404

    archived = crud.archive_project(g.db_conn, project_id, g.user_id)
    if not archived:
        return jsonify({"error": "Project already archived"}), 409

    return jsonify({"status": "archived", "project_id": project_id}), 200


@app.route("/projects/archived", methods=["GET"])
def get_archived_projects():
    projects = crud.get_archived_projects(g.db_conn, g.user_id)
    return jsonify(projects), 200


@app.route("/projects/<int:project_id>", methods=["GET"])
def get_project(project_id: int):
    project = crud.get_project(g.db_conn, project_id, g.user_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404
    return jsonify(project), 200


@app.route("/projects/<int:project_id>", methods=["DELETE"])
def delete_project(project_id: int):
    if not crud.project_exists(g.db_conn, project_id, g.user_id):
        return jsonify({"error": "Project not found"}), 404

    archived = crud.archive_project(g.db_conn, project_id, g.user_id)
    if not archived:
        return jsonify({"error": "Project already archived"}), 409

    return jsonify({"status": "archived", "project_id": project_id}), 200


@app.route("/projects/<int:project_id>/restore", methods=["POST"])
def restore_project(project_id: int):
    if not crud.project_exists(g.db_conn, project_id, g.user_id):
        return jsonify({"error": "Project not found"}), 404

    restored = crud.restore_project(g.db_conn, project_id, g.user_id)
    if not restored:
        return jsonify({"error": "Project is not archived"}), 409

    return jsonify({"status": "restored", "project_id": project_id}), 200


@app.route("/projects/<int:project_id>/goals/today", methods=["GET"])
def get_todays_goal(project_id: int):
    if not crud.project_exists(g.db_conn, project_id, g.user_id):
        return jsonify({"error": "Project not found"}), 404

    goal = crud.get_todays_goal(g.db_conn, project_id, g.user_id)
    if not goal:
        return jsonify({"error": "No goal set for today"}), 404

    goal["created_at"] = to_iso(goal.get("created_at"))
    return jsonify(goal), 200


@app.route("/projects/<int:project_id>/goals/today", methods=["PUT"])
def upsert_today_goal(project_id):
    if not crud.project_exists(g.db_conn, project_id, g.user_id):
        return jsonify({"error": "Project not found"}), 404

    data = request.get_json()
    goal_text = data.get("goal_text")

    if not goal_text:
        return jsonify({"error": "goal_text required"}), 400

    row = crud.upsert_daily_goal_today(g.db_conn, project_id, g.user_id, goal_text)

    status_code = 201 if row["inserted"] else 200
    row.pop("inserted", None)
    return jsonify(row), status_code


@app.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "email and password required"}), 400

    existing = crud.get_user_by_email(g.db_conn, email)
    if existing:
        return jsonify({"error": "Email already registered"}), 409

    user = crud.create_user(g.db_conn, email, password)
    return jsonify(user), 201


@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "email and password required"}), 400

    user = crud.verify_user_password(g.db_conn, email, password)
    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    refresh = crud.create_refresh_token(g.db_conn, user["id"])

    return jsonify({
        "id": user["id"],
        "email": user["email"],
        "token": user["token"],
        "refresh_token": refresh["token"],
    }), 200


@app.route("/auth/logout", methods=["POST"])
def logout():
    data = request.get_json(silent=True) or {}
    refresh_token = data.get("refresh_token")

    if not refresh_token:
        return jsonify({"error": "refresh_token required"}), 400

    revoked = crud.revoke_refresh_token(g.db_conn, g.user_id, refresh_token)
    if not revoked:
        return jsonify({"error": "Refresh token not found or already revoked"}), 404

    return jsonify({"status": "logged_out"}), 200


if __name__ == "__main__":
    app.run(debug=True)