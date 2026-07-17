from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from app.config import Config
from app.extensions import db, migrate, jwt
from app.products.routes import products_bp
from app.auth.routes import auth_bp
from app.errors.handlers import register_error_handlers

from  app.payments.routes import payments_bp
from app.logging_config import configure_logging

def create_app():
    app = Flask(__name__)

    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/apispec.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/",
    }

    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "SaaS Payment API",
            "description": (
                "REST API for the SaaS Payment Platform.\n\n"
                "Supports JWT Authentication, Stripe Payments, "
                "Redis, Celery and Resend Email."
            ),
            "version": "1.0.0",
            "contact": {
                "name": "Yashank Saluja",
                "email": "yashanksaluja8@gmail.com"
            }
        },

        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description":
                    "Enter: Bearer <JWT Token>"
            }
        }
    }

    Swagger(
        app,
        config=swagger_config,
        template=swagger_template,
    )

    app.config.from_object(Config)

    configure_logging()
    
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
    app.register_blueprint(
        payments_bp,
        url_prefix="/api/payments"
    )
    register_error_handlers(app)
    return app