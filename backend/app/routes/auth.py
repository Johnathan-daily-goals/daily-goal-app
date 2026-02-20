from flask import Blueprint, request, jsonify, g, current_app
from itsdangerous import URLSafeTimedSerializer

from backend.app import crud


blueprint = Blueprint("auth", __name__, url_prefix="/auth")


def _token_serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(current_app.config["ACCESS_TOKEN_SECRET"])


def generate_access_token(user_id: int) -> str:
    serializer = _token_serializer()
    return serializer.dumps({"user_id": user_id})


@blueprint.route("/register", methods=["POST"])
def register():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    if not email or not password:
        return jsonify({"error": "email and password required"}), 400

    existing_user = crud.get_user_by_email(g.db_conn, email)
    if existing_user:
        return jsonify({"error": "Email already registered"}), 409

    created_user = crud.create_user(g.db_conn, email, password)

    access_token_row = crud.create_access_token(
        g.db_conn,
        created_user["id"],
        ttl_seconds=current_app.config["ACCESS_TOKEN_TTL_SECONDS"],
    )
    refresh_token_row = crud.create_refresh_token(g.db_conn, created_user["id"])
    return jsonify(
        {
            "id": created_user["id"],
            "email": created_user["email"],
            "access_token": access_token_row["token"],
            "refresh_token": refresh_token_row["token"],
            "expires_in": current_app.config["ACCESS_TOKEN_TTL_SECONDS"],
        }
    ), 201


@blueprint.route("/login", methods=["POST"])
def login():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    if not email or not password:
        return jsonify({"error": "email and password required"}), 400

    user = crud.verify_user_password(g.db_conn, email, password)
    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    access_token_row = crud.create_access_token(
        g.db_conn,
        user["id"],
        ttl_seconds=current_app.config["ACCESS_TOKEN_TTL_SECONDS"],
    )
    refresh_token_row = crud.create_refresh_token(g.db_conn, user["id"])
    return jsonify(
        {
            "id": user["id"],
            "email": user["email"],
            "access_token": access_token_row["token"],
            "refresh_token": refresh_token_row["token"],
            "expires_in": current_app.config["ACCESS_TOKEN_TTL_SECONDS"],
        }
    ), 200


@blueprint.route("/refresh", methods=["POST"])
def refresh():
    payload = request.get_json(silent=True) or {}
    provided_refresh_token = payload.get("refresh_token")

    if not provided_refresh_token:
        return jsonify({"error": "refresh_token required"}), 400

    refresh_result = crud.use_refresh_token(g.db_conn, provided_refresh_token)
    if not refresh_result:
        return jsonify({"error": "Invalid or expired refresh token"}), 401

    access_token_row = crud.create_access_token(
        g.db_conn,
        refresh_result["user_id"],
        ttl_seconds=current_app.config["ACCESS_TOKEN_TTL_SECONDS"],
    )
    return jsonify(
        {
            "access_token": access_token_row["token"],
            "refresh_token": refresh_result["refresh_token"],
            "expires_at": refresh_result["expires_at"],
        }
    ), 200


@blueprint.route("/logout", methods=["POST"])
def logout():
    payload = request.get_json(silent=True) or {}
    provided_refresh_token = payload.get("refresh_token")

    if not provided_refresh_token:
        return jsonify({"error": "refresh_token required"}), 400

    authorization_header = request.headers.get("Authorization", "")
    provided_access_token = ""
    if authorization_header.startswith("Bearer "):
        provided_access_token = authorization_header.removeprefix("Bearer ").strip()

    refresh_was_revoked = crud.revoke_refresh_token_by_token(
        g.db_conn,
        provided_refresh_token,
    )

    access_was_revoked = False
    if provided_access_token:
        access_was_revoked = crud.revoke_access_token_by_token(
            g.db_conn,
            provided_access_token,
        )

    # Don't fail logout if tokens are already expired/revoked/missing in DB.
    return jsonify(
        {
            "status": "logged_out",
            "refresh_token_revoked": refresh_was_revoked,
            "access_token_revoked": access_was_revoked,
        }
    ), 200
