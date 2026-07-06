import os

import stripe
from dotenv import load_dotenv


load_dotenv()


stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


PRODUCTS = [
    {
        "name": "SaaS Starter",
        "description": "Starter access to the SaaS project",
        "tier": "starter",
        "lookup_key": "saas_starter",
        "unit_amount": 99900,
        "currency": "inr",
    },
    {
        "name": "SaaS Pro",
        "description": "Complete access to the SaaS project",
        "tier": "pro",
        "lookup_key": "saas_pro",
        "unit_amount": 199900,
        "currency": "inr",
    },
]


def find_price_by_lookup_key(lookup_key):
    prices = stripe.Price.list(
        lookup_keys=[lookup_key],
        active=True,
        limit=1,
    )

    if prices.data:
        return prices.data[0]

    return None


def seed_stripe_products():
    for product_data in PRODUCTS:
        existing_price = find_price_by_lookup_key(
            product_data["lookup_key"]
        )

        if existing_price:
            print(
                f"Skipping {product_data['name']} - "
                "price already exists"
            )

            continue

        product = stripe.Product.create(
            name=product_data["name"],
            description=product_data["description"],
            metadata={
                "tier": product_data["tier"]
            },
        )

        price = stripe.Price.create(
            product=product.id,
            unit_amount=product_data["unit_amount"],
            currency=product_data["currency"],
            lookup_key=product_data["lookup_key"],
        )

        print(
            f"Created {product.name} "
            f"with price {price.id}"
        )


if __name__ == "__main__":
    seed_stripe_products()