from flask import Flask
from flask_cors import CORS
from app.config import Config

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    CORS(app)

    @app.route("/")
    def home():
        return {
            "message": "SaaS Payment API is running"
        }

    return app