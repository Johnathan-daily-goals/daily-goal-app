from flask import Flask, request, jsonify, g
from flask_cors import CORS
from backend.app.database import Database
from backend.app import crud
from backend.app.errors import AppError, Unauthorized
import os
from backend.app.routes.auth import blueprint as auth_blueprint
from datetime import datetime, timezone



app = Flask(__name__)
CORS(app)  # Allow all origins in dev; restrict in production
app.config["ACCESS_TOKEN_SECRET"] = os.getenv(
    "ACCESS_TOKEN_SECRET", "dev-only-change-me"
)
app.config["ACCESS_TOKEN_TTL_SECONDS"] = int(
    os.getenv("ACCESS_TOKEN_TTL_SECONDS", "900")
)

app.register_blueprint(auth_blueprint)
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
    if request.path == "/health" or request.path.startswith("/auth/"):
        return

    authorization_header = request.headers.get("Authorization", "")
    if not authorization_header.startswith("Bearer "):
        raise Unauthorized("Missing or invalid Authorization header")

    access_token_value = authorization_header.removeprefix("Bearer ").strip()
    if not access_token_value:
        raise Unauthorized("Missing or invalid Authorization header")

    token_row = crud.get_valid_access_token(g.db_conn, access_token_value)
    if not token_row:
        raise Unauthorized("Invalid or expired token")

    g.user_id = token_row["user_id"]


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

    return jsonify({"id": project_id, "name": name, "description": description}), 201


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

    return jsonify(
        {"id": goal_id, "project_id": project_id, "goal_text": goal_text}
    ), 201


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


if __name__ == "__main__":
    # Port 5000 is taken by macOS AirPlay Receiver on Monterey+
    app.run(debug=True, port=8000)
