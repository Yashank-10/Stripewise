from flask import Blueprint
from app.products.services import get_all_products

products_bp = Blueprint(
    "products",
    __name__
)


@products_bp.route("/", methods=["GET"])
def get_products():
    """
    List Available Products
    ---
    tags:
      - Products

    summary: Get all available SaaS products.

    description: |
      Returns all available subscription products
      that users can purchase.

    produces:
      - application/json

    responses:
      200:
        description: Products retrieved successfully.
        schema:
          type: object
          properties:
            products:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: string
                  name:
                    type: string
                  tier:
                    type: string
                  price:
                    type: integer
                  currency:
                    type: string
                  description:
                    type: string

    """

    products = get_all_products()

    return {
        "products": products
    }, 200