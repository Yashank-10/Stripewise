from flask import Blueprint, request

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)

from app.payments.services import (
    create_checkout_session,
)

payments_bp = Blueprint(
    "payments",
    __name__,
)


@payments_bp.route("/health", methods=["GET"])
def health():
    return {
        "message": "Payments module is working"
    }, 200


@payments_bp.route(
    "/create-checkout-session",
    methods=["POST"],
)
@jwt_required()
def checkout():

    data = request.get_json() or {}

    tier = data.get("tier")

    if not tier:
        return {
            "error": "Tier is required"
        }, 400

    user_id = get_jwt_identity()

    try:

        checkout_session = create_checkout_session(
            user_id=user_id,
            tier=tier,
        )

        return {
            "checkout_url": checkout_session.url
        }, 200

    except Exception as e:

        return {
            "error": str(e)
        }, 400