from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.extensions import db, migrate, jwt
from app.products.routes import products_bp
from app.auth.routes import auth_bp

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    CORS(app)

    db.init_app(app)

    migrate.init_app(app, db)

    jwt.init_app(app)

    from app import models

    app.register_blueprint(
        products_bp,
        url_prefix="/api/products"
    )

    app.register_blueprint(
        auth_bp,
        url_prefix="/api/auth"
    )

    return app