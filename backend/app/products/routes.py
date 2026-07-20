from flask import Blueprint
from app.products.services import get_all_products
from app.core.responses import success_response

products_bp = Blueprint("products", __name__)

@products_bp.route("/", methods=["GET"])
def get_products():
    
    products = get_all_products()

    return success_response(
        message="Products fetched successfully.",
        data={
            "products": products
        }
    )