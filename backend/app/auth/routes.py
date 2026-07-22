import logging
from app.auth.serializers import serialize_user
from flask import Blueprint, request
from app.extensions import db
from app.models.user import User
from app.core.responses import success_response, error_response
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
)

from app.auth.services import (
    authenticate_user,
    register_user,
)

auth_bp = Blueprint(
    "auth",
    __name__
)

logger = logging.getLogger(__name__)
@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a New User
    ---
    tags:
      - Authentication

    summary: Register a new user.

    description: |
      Creates a new user account and returns
      a JWT access token upon successful registration.

    consumes:
      - application/json

    produces:
      - application/json

    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            name:
              type: string
              example: Yashank Saluja
            email:
              type: string
              example: yashank@example.com
            password:
              type: string
              example: StrongPassword123

    responses:
      201:
        description: User registered successfully.
        schema:
          type: object
          properties:
            message:
              type: string
              example: User registered successfully
            access_token:
              type: string
            user:
              type: object
              properties:
                id:
                  type: string
                email:
                  type: string
                name:
                  type: string

      400:
        description: Invalid request.

      409:
        description: Email already exists.
    """
    data = request.get_json() or {}

    email = data.get("email")
    password = data.get("password")
    name = data.get("name")

    if not email or not password:
        logger.warning(
            "Registration failed: email or password missing"
        )
        return error_response("Email and password are required"), 400

    if len(password) < 8:
        logger.warning(
            "Registration failed: password too short for email %s",
            email,
        )
        return error_response("Password must be at least 8 characters"), 400

    user, error = register_user(
        email=email,
        password=password,
        name=name,
    )

    if error:
        logger.warning(
            "Registration failed for email %s: %s",
            email,
            error,
        )
        return error_response(error), 409

    access_token = create_access_token(
        identity=user.id
    )
    logger.info(
        "User registered successfully (id=%s, email=%s)",
        user.id,
        user.email,
    )

    return success_response(
        message="User registered successfully",
        data={
            "user": serialize_user(user)
        }
    ), 201
@auth_bp.route("/login", methods=["POST"])
def login():
    """
    User Login
    ---
    tags:
        - Authentication

    summary: Authenticate an existing user.

    description: |
        Validates user credentials and returns
        a JWT access token.

    consumes:
        - application/json

    produces:
        - application/json

    parameters:
      - in: body
        name: body
        required: true
        schema:
            type: object
            required:
                - email
                - password
            properties:
                email:
                    type: string
                    example: yashank@example.com
                password:
                    type: string
                    example: StrongPassword123

    responses:
        200:
            description: Login successful.
        401:
            description: Invalid email or password.

        400:
            description: Missing credentials.
    """
    data = request.get_json() or {}

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        logger.warning(
            "Login failed: email or password missing"
        )
        return {
            "error": "Email and password are required"
        }, 400

    user = authenticate_user(
        email=email,
        password=password,
    )

    if not user:
        logger.warning(
            "Invalid login attempt for email %s",
            email,
        )
        return {
            "error": "Invalid email or password"
        }, 401

    access_token = create_access_token(
        identity=user.id
    )
    logger.info(
        "User logged in successfully (id=%s)",
        user.id,
    )
    user_data = {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
    }

    return success_response(
        message="Login successful.",
        data={
            "access_token": access_token,
            "user": serialize_user(user),
        }
    ) 

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """
    Get Current User
    ---
    tags:
      - Authentication

    summary: Get the currently authenticated user.

    description: |
      Returns the profile of the authenticated user.
      This endpoint requires a valid JWT access token.

    produces:
      - application/json

    security:
      - Bearer: []

    responses:
      200:
        description: User details retrieved successfully.
        schema:
          type: object
          properties:
            user:
              type: object
              properties:
                id:
                  type: string
                email:
                  type: string
                name:
                  type: string
                github_username:
                  type: string
                email_verified:
                  type: boolean

      401:
        description: Unauthorized (invalid or missing JWT token)

      404:
        description: User not found.
    """

    user_id = get_jwt_identity()

    user = db.session.get(
        User,
        user_id
    )

    if not user:
        return {
            "error": "User not found"
        }, 404

    return success_response(
        message="User profile fetched successfully.",
        data={
            "user": serialize_user(user),
        }
    )