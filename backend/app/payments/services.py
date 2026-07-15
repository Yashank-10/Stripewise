import stripe
import logging
from flask import current_app
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.purchase import Purchase
from app.models.user import User
from app.payments.constants import TIER_LOOKUP_KEYS
from app.payments.provisioning import provision_purchase

logger = logging.getLogger(__name__)

def initialize_stripe():
    stripe.api_key = current_app.config[
        "STRIPE_SECRET_KEY"
    ]

    logger.debug("Stripe SDK initialized.")


def get_price_by_lookup_key(lookup_key):
    logger.debug(
        "Fetching Stripe price for lookup key '%s'",
        lookup_key,
    )
    initialize_stripe()

    prices = stripe.Price.list(
        lookup_keys=[lookup_key],
        active=True,
        limit=1,
    )
    logger.info(
        "Stripe returned %d prices for lookup key '%s'",
        len(prices.data),
        lookup_key,
    )
    logger.info(
        "Lookup key being searched: %s",
        lookup_key,
    )

    if not prices.data:
        logger.warning(
            "Stripe price not found for lookup key '%s'",
            lookup_key,
        )
        return None

    return prices.data[0]


def create_checkout_session(user_id, tier):
    initialize_stripe()
    logger.info(
        "Creating checkout session for user %s (tier=%s)",
        user_id,
        tier,
    )
    if tier not in TIER_LOOKUP_KEYS:
        logger.warning(
            "Invalid subscription tier requested: %s",
            tier,
        )
        raise ValueError("Invalid subscription tier")

    lookup_key = TIER_LOOKUP_KEYS[tier]

    price = get_price_by_lookup_key(
        lookup_key
    )

    if not price:
        logger.error(
            "Stripe price missing for tier '%s'",
            tier,
        )
        raise ValueError("Stripe price missing for tier")

    checkout_session = (
        stripe.checkout.Session.create(
            mode="payment",
            line_items=[
                {
                    "price": price.id,
                    "quantity": 1,
                }
            ],
            success_url=(
                "http://localhost:3000/"
                "payment/success"
                "?session_id={CHECKOUT_SESSION_ID}"
            ),
            cancel_url=(
                "http://localhost:3000/"
                "payment/cancel"
            ),
            metadata={
                "user_id": user_id,
                "tier": tier,
            },
        )
    )
    logger.info(
        "Checkout session %s created successfully",
        checkout_session.id,
    )
    return checkout_session


def handle_checkout_completed(session):
    checkout_session_id = session["id"]

    logger.info(
        "Processing completed checkout session %s",
        checkout_session_id,
    ) 

    existing_purchase = Purchase.query.filter_by(
        checkout_session_id=checkout_session_id
    ).first()

    if existing_purchase:
        logger.warning(
            "Duplicate webhook detected for session %s",
            checkout_session_id,
    )

        return existing_purchase, False

    metadata = session["metadata"]

    user_id = metadata["user_id"]
    tier = metadata["tier"]

    if not user_id:
        logger.warning(
            "Checkout session missing user_id"
        )
        raise ValueError(
            "Checkout session is missing user_id"
        )

    if not tier:
        logger.warning(
            "Checkout session missing tier"
        )
        raise ValueError(
            "Checkout session is missing tier"
        )

    if tier not in TIER_LOOKUP_KEYS:
        logger.warning(
            "Invalid tier '%s' in checkout metadata",
             tier,
      )
        raise ValueError(
            "Invalid tier in checkout metadata"
        )

    user = db.session.get(
        User,
        user_id
    )

    if not user:
        logger.error(
            "User %s not found during webhook processing",
            user_id,
        )
        raise ValueError(
            "User not found"
        )

    amount_total = session["amount_total"]

    currency = session["currency"]

    if amount_total is None:
        logger.error(
            "Checkout session %s is missing amount",
            checkout_session_id,
        )
        raise ValueError(
            "Checkout session is missing amount"
        )

    if not currency:
        logger.error(
            "Checkout session %s is missing currency",
            checkout_session_id,
        )
        raise ValueError(
            "Checkout session is missing currency"
        )

    purchase = Purchase(
        user_id=user_id,
        checkout_session_id=checkout_session_id,
        tier=tier,
        amount=amount_total,
        currency=currency,
        status="completed",
    )
    logger.info(
        "Purchase created for user %s",
        user_id,
    )

    db.session.add(purchase)
    try:
        db.session.commit()
        logger.info(
            "Purchase %s committed successfully",
            purchase.id,
        )

    except IntegrityError:
        logger.warning(
            "Duplicate purchase detected for checkout session %s",
            checkout_session_id,
        )
        db.session.rollback()

        existing_purchase = (
            Purchase.query.filter_by(
                checkout_session_id=(
                    checkout_session_id
                )
            ).first()
        )

        if existing_purchase:
            provision_purchase(
                existing_purchase
            )

            return existing_purchase, False

        raise
    from app.tasks.payment_tasks import provision_purchase_task
    from app.tasks.email_tasks import send_purchase_confirmation_task
    logger.info(
        "Queueing provisioning task for purchase %s",
        purchase.id,
    )
    provision_purchase_task.delay(purchase.id)
    logger.info(
        "Queueing purchase confirmation email for purchase %s",
        purchase.id,
    )
    send_purchase_confirmation_task.delay(
        purchase.id
    )
    return purchase, True

def claim_purchase(user_id, checkout_session_id):
    purchase = Purchase.query.filter_by(
        checkout_session_id=checkout_session_id
    ).first()

    if not purchase:
        logger.warning(
            "Purchase not found for checkout session %s",
            checkout_session_id,
        )
        return None, "Purchase not found"

    if purchase.user_id != user_id:
        logger.warning(
            "User %s attempted to claim purchase %s",
            user_id,
            checkout_session_id,
        )
        return None, "Purchase does not belong to user"

    if purchase.status != "completed":
        logger.warning(
            "Attempt to claim incomplete purchase %s",
            purchase.id,
        )
        return None, "Payment is not completed"
    logger.info(
        "Purchase %s successfully claimed by user %s",
        purchase.id,
        user_id,
    )
    return purchase, None 