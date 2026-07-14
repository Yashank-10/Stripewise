import logging

from app.celery_app import celery
from app.models.purchase import Purchase
from app.models.user import User
from app.emails.service import send_purchase_confirmation

logger = logging.getLogger(__name__)

# sends purchase confirmation email to customer after successful payment
@celery.task(bind=True, max_retries=3)
def send_purchase_confirmation_task(self, purchase_id):
  
    logger.info(
        "Email task started for purchase %s",
        purchase_id,
    )

    try:
        purchase = Purchase.query.get(purchase_id)

        if purchase is None:
            logger.error(
                "Purchase %s not found",
                purchase_id,
            )
            raise ValueError(
                f"Purchase '{purchase_id}' not found."
            )

        user = User.query.get(purchase.user_id)

        if user is None:
            logger.error(
                "User %s not found",
                purchase.user_id,
            )
            raise ValueError(
                f"User '{purchase.user_id}' not found."
            )

        response = send_purchase_confirmation(
            customer_name=user.name,
            customer_email=user.email,
            tier=purchase.tier,
        )

        logger.info(
            "Purchase confirmation email queued successfully for %s",
            user.email,
        )

        return response

    except Exception:
        logger.exception(
            "Failed to send purchase confirmation email for purchase %s",
            purchase_id,
        )
        raise