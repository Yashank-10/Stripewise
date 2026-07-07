from flask import Blueprint, request
from app.extensions import db
from app.models.user import User
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
)

from app.auth.services import (
    authenticate_user,
    register_user,
)
from app.models.user import User


auth_bp = Blueprint(
    "auth",
    __name__
)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}

    email = data.get("email")
    password = data.get("password")
    name = data.get("name")

    if not email or not password:
        return {
            "error": "Email and password are required"
        }, 400

    if len(password) < 8:
        return {
            "error": "Password must be at least 8 characters"
        }, 400

    user, error = register_user(
        email=email,
        password=password,
        name=name,
    )

    if error:
        return {
            "error": error
        }, 409

    access_token = create_access_token(
        identity=user.id
    )

    return {
        "message": "User registered successfully",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
        }
    }, 201
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return {
            "error": "Email and password are required"
        }, 400

    user = authenticate_user(
        email=email,
        password=password,
    )

    if not user:
        return {
            "error": "Invalid email or password"
        }, 401

    access_token = create_access_token(
        identity=user.id
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
        }
    }, 200

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()

    user = db.session.get(
        User,
        user_id
    )

    if not user:
        return {
            "error": "User not found"
        }, 404

    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "github_username": user.github_username,
            "email_verified": user.email_verified,
        }
    }, 200