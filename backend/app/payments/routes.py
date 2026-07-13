import stripe
import logging

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
    claim_purchase,
    create_checkout_session,
    handle_checkout_completed,
)


payments_bp = Blueprint(
    "payments",
    __name__,
)

logger  = logging.getLogger (__name__)
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
        checkout_session = create_checkout_session(
                user_id=user_id,
                tier=tier,
        )
        logger.info(
            "Checkout session created for user %s (tier=%s, session_id=%s)",
            user_id,
            tier,
            checkout_session.id,
        )

        return {
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id,
        }, 200

    except ValueError as error:
        return {
            "error": str(error)
        }, 400

    except stripe.StripeError:
        logger.exception(
            "Stripe checkout session creation failed for user %s",
            user_id,
        )

        return {
            "error": "Unable to create checkout session"
        }, 502

@payments_bp.route(
    "/claim",
    methods=["POST"],
)
@jwt_required()
def claim():
    data = request.get_json() or {}

    checkout_session_id = data.get(
        "session_id"
    )

    if not checkout_session_id:
        return {
            "error": "Session ID is required"
        }, 400

    user_id = get_jwt_identity()

    purchase, error = claim_purchase(
        user_id=user_id,
        checkout_session_id=(
            checkout_session_id
        ),
    )

    if error == "Purchase not found":
        return {
            "error": error
        }, 404

    if error == (
        "Purchase does not belong to user"
    ):
        return {
            "error": "Purchase access denied"
        }, 403

    if error:
        return {
            "error": error
        }, 409
    logger.info(
        "Purchase %s successfully claimed by user %s",
        purchase.id,
        user_id,
)

    return {
        "message": "Purchase found",
        "purchase": {
            "id": purchase.id,
            "tier": purchase.tier,
            "amount": purchase.amount,
            "currency": purchase.currency,
            "status": purchase.status,
            "access_status": (
                purchase.access_status
            ),
        }
    }, 200

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
        logger.info(
            "Received Stripe webhook: %s",
            event["type"],
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
                logger.info(
                    "Purchase created successfully: %s",
                    purchase.id,
                )

            else:
                logger.warning(
                    "Duplicate webhook ignored for purchase %s",
                    purchase.id,
                )

    except ValueError as error:
        logger.warning(
            "Webhook validation failed: %s",
            str(error),
        )

        return {
            "error": str(error)
        }, 400

    except Exception as error:
        logger.exception(
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