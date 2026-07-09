import stripe

from flask import current_app
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.purchase import Purchase
from app.models.user import User
from app.payments.constants import TIER_LOOKUP_KEYS


def initialize_stripe():
    stripe.api_key = current_app.config[
        "STRIPE_SECRET_KEY"
    ]


def get_price_by_lookup_key(lookup_key):
    initialize_stripe()

    prices = stripe.Price.list(
        lookup_keys=[lookup_key],
        active=True,
        limit=1,
    )

    if not prices.data:
        return None

    return prices.data[0]


def create_checkout_session(user_id, tier):
    initialize_stripe()

    if tier not in TIER_LOOKUP_KEYS:
        raise ValueError("Invalid subscription tier")

    lookup_key = TIER_LOOKUP_KEYS[tier]

    price = get_price_by_lookup_key(
        lookup_key
    )

    if not price:
        raise ValueError(
            "Stripe price not found"
        )

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

    return checkout_session


def handle_checkout_completed(session):
    checkout_session_id = session["id"]

    existing_purchase = Purchase.query.filter_by(
        checkout_session_id=checkout_session_id
    ).first()

    if existing_purchase:
        return existing_purchase, False

    metadata = session.get("metadata") or {}

    user_id = metadata.get("user_id")
    tier = metadata.get("tier")

    if not user_id:
        raise ValueError(
            "Checkout session is missing user_id"
        )

    if not tier:
        raise ValueError(
            "Checkout session is missing tier"
        )

    if tier not in TIER_LOOKUP_KEYS:
        raise ValueError(
            "Invalid tier in checkout metadata"
        )

    user = db.session.get(
        User,
        user_id
    )

    if not user:
        raise ValueError(
            "User not found"
        )

    amount_total = session.get(
        "amount_total"
    )

    currency = session.get(
        "currency"
    )

    if amount_total is None:
        raise ValueError(
            "Checkout session is missing amount"
        )

    if not currency:
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

    db.session.add(purchase)

    try:
        db.session.commit()

    except IntegrityError:
        db.session.rollback()

        existing_purchase = (
            Purchase.query.filter_by(
                checkout_session_id=(
                    checkout_session_id
                )
            ).first()
        )

        if existing_purchase:
            return existing_purchase, False

        raise

    return purchase, True