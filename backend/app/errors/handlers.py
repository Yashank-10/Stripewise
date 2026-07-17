from flask import jsonify
import logging

logger = logging.getLogger(__name__)


def register_error_handlers(app):

    @app.errorhandler(ValueError)
    def handle_value_error(error):

        logger.warning(str(error))

        return jsonify({
            "success": False,
            "error": str(error)
        }), 400


    @app.errorhandler(Exception)
    def handle_unexpected_error(error):

        logger.exception(
            "Unhandled exception"
        )

        return jsonify({
            "success": False,
            "error": "Internal Server Error"
        }), 500