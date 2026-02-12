from flask import Flask, request, jsonify, g
from backend.app.database import Database
from backend.app import crud
from backend.app.errors import AppError

app = Flask(__name__)
database = Database()


# Open connection before each request
@app.before_request
def open_db_connection():
    g.db_conn = database.get_connection()


# Close connection after each request
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
    description = data.get("description")  # optional

    if not name:
        return jsonify({"error": "Project name required"}), 400

    project_id = crud.create_project(g.db_conn, name, description)

    return jsonify({
        "id": project_id,
        "name": name,
        "description": description
    }), 201


@app.route("/projects", methods=["GET"])
def get_projects():
    projects = crud.get_projects(g.db_conn)
    return jsonify(projects), 200


@app.route("/projects/<int:project_id>/goals", methods=["POST"])
def create_daily_goal(project_id):
    project = crud.get_project(g.db_conn, project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    data = request.get_json()
    goal_text = data.get("goal_text")

    if not goal_text:
        return jsonify({"error": "goal_text required"}), 400

    goal_id = crud.create_daily_goal(g.db_conn, project_id, goal_text)

    return jsonify({
        "id": goal_id,
        "project_id": project_id,
        "goal_text": goal_text
    }), 201


@app.route("/projects/<int:project_id>/goals", methods=["GET"])
def get_daily_goals(project_id):
    project = crud.get_project(g.db_conn, project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    goals = crud.get_daily_goals(g.db_conn, project_id)
    return jsonify(goals), 200


if __name__ == "__main__":
    app.run(debug=True)

