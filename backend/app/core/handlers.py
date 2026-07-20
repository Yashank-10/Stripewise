from app.core.responses import error_response
from app.core.exceptions import AppException

import logging

logger = logging.getLogger(__name__)


def register_error_handlers(app):

    @app.errorhandler(AppException)
    def handle_app_exception(error):

        logger.warning(error.message)

        return error_response(
            message=error.message,
            status_code=error.status_code,
        )


    @app.errorhandler(Exception)
    def handle_unexpected_exception(error):

        logger.exception("Unhandled exception")

        return error_response(
            message="Internal Server Error",
            status_code=500,
        )