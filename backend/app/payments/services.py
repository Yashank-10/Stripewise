import stripe

from flask import current_app

from app.payments.constants import TIER_LOOKUP_KEYS


def initialize_stripe():
    stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]


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

    price = get_price_by_lookup_key(lookup_key)

    if not price:
        raise ValueError("Stripe price not found")

    checkout_session = stripe.checkout.Session.create(
        mode="payment",

        line_items=[
            {
                "price": price.id,
                "quantity": 1,
            }
        ],

        success_url="http://localhost:3000/payment/success?session_id={CHECKOUT_SESSION_ID}",

        cancel_url="http://localhost:3000/payment/cancel",

        metadata={
            "user_id": user_id,
            "tier": tier,
        },
    )

    return checkout_session