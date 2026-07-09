import stripe

from flask import (
    Blueprint,
    current_app,
    request,
)
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
)

from app.payments.services import (
    create_checkout_session,
    handle_checkout_completed,
)


payments_bp = Blueprint(
    "payments",
    __name__,
)


@payments_bp.route(
    "/health",
    methods=["GET"],
)
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
        checkout_session = (
            create_checkout_session(
                user_id=user_id,
                tier=tier,
            )
        )

        return {
            "checkout_url": (
                checkout_session.url
            )
        }, 200

    except ValueError as error:
        return {
            "error": str(error)
        }, 400

    except stripe.StripeError:
        return {
            "error": (
                "Unable to create checkout session"
            )
        }, 502


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

    try:
        if (
            event["type"]
            == "checkout.session.completed"
        ):
            session = event["data"]["object"]

            purchase, created = (
                handle_checkout_completed(
                    session
                )
            )

            if created:
                print(
                    "Purchase created:",
                    purchase.id
                )

            else:
                print(
                    "Purchase already processed:",
                    purchase.id
                )

    except ValueError as error:
        print(
            "Webhook processing error:",
            str(error)
        )

        return {
            "error": str(error)
        }, 400

    except Exception as error:
        current_app.logger.exception(
            "Unexpected webhook processing error"
        )

        return {
            "error": (
                "Webhook processing failed"
            )
        }, 500

    return {
        "received": True
    }, 200