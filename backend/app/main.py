from flask import Flask, request, jsonify, g
from app.database import Database
from app import crud

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


@app.route("/projects", methods=["POST"])
def create_project():
    data = request.get_json()
    name = data.get("name")

    if not name:
        return jsonify({"error": "Project name required"}), 400

    project_id = crud.create_project(g.db_conn, name)

    return jsonify({"id": project_id, "name": name}), 201


@app.route("/projects", methods=["GET"])
def get_projects():
    projects = crud.get_projects(g.db_conn)
    return jsonify(projects), 200