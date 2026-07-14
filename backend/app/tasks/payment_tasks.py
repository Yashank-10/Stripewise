import logging

from app.celery_app import celery
from app.models.purchase import Purchase
from app.payments.provisioning import provision_purchase

logger = logging.getLogger(__name__)


@celery.task(bind=True, max_retries=3)
def provision_purchase_task(self, purchase_id):
    logger.info(
        "Background provisioning task started for purchase %s",
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

        entitlement, created = provision_purchase(purchase)

        logger.info(
            "Provisioned purchase %s successfully (created=%s)",
            purchase.id,
            created,
        )

        return {
            "purchase_id": purchase.id,
            "created": created,
        }

    except Exception:
        logger.exception(
            "Background provisioning failed for purchase %s",
            purchase_id,
        )
        raise