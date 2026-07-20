from flask import jsonify
import logging

from app.core.exceptions import AppException

logger = logging.getLogger(__name__)


def register_error_handlers(app):

    @app.errorhandler(AppException)
    def handle_app_exception(error):

        logger.warning(error.message)

        return jsonify({
            "success": False,
            "error": error.message
        }), error.status_code


    @app.errorhandler(Exception)
    def handle_unexpected_exception(error):

        logger.exception(
            "Unhandled application exception"
        )

        return jsonify({
            "success": False,
            "error": "Internal Server Error"
        }), 500