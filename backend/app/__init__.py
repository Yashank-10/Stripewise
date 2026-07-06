from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.extensions import db, migrate
from app.products.routes import products_bp


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    CORS(app)

    db.init_app(app)

    migrate.init_app(app, db)

    from app import models

    app.register_blueprint(
        products_bp,
        url_prefix="/api/products"
    )

    return app