from flask import Blueprint

from app.products.services import get_all_products


products_bp = Blueprint(
    "products",
    __name__
)


@products_bp.route("/", methods=["GET"])
def get_products():
    products = get_all_products()

    return {
        "products": products
    }, 200