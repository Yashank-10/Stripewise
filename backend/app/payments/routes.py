from flask import Blueprint, request

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)

from app.payments.services import (
    create_checkout_session,
)

import stripe

from flask import (
    Blueprint,
    current_app,
    request,
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

@payments_bp.route(
    "/webhook",
    methods=["POST"],
)
def stripe_webhook():
    payload = request.get_data()

    signature = request.headers.get(
        "Stripe-Signature"
    )

    webhook_secret = current_app.config[
        "STRIPE_WEBHOOK_SECRET"
    ]

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=signature,
            secret=webhook_secret,
        )

    except ValueError:
        return {
            "error": "Invalid webhook payload"
        }, 400

    except stripe.SignatureVerificationError:
        return {
            "error": "Invalid webhook signature"
        }, 400

    print(
        "Stripe event received:",
        event["type"]
    )

    return {
        "received": True
    }, 200