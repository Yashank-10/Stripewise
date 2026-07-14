import logging
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.entitlement import Entitlement

logger = logging.getLogger(__name__)

SUPPORTED_TIERS = {
    "starter",
    "pro",
}


def provision_purchase(purchase):
    logger.info(
        "Starting provisioning for purchase %s",
        purchase.id,
    )
    if purchase.status != "completed":
        logger.warning(
            "Attempted to provision incomplete purchase %s (status=%s)",
            purchase.id,
            purchase.status,
    )
        raise ValueError(
            "Cannot provision an incomplete purchase"
        )

    if purchase.tier not in SUPPORTED_TIERS:
        logger.warning(
            "Unsupported purchase tier '%s' for purchase %s",
            purchase.tier,
            purchase.id,
        )
        raise ValueError(
            "Unsupported purchase tier"
        )

    existing_entitlement = (
        Entitlement.query.filter_by(
            purchase_id=purchase.id
        ).first()
    )

    if existing_entitlement:
        if purchase.access_status != "granted":
            purchase.access_status = "granted"
            db.session.commit()

        logger.info(
            "Entitlement already exists for purchase %s",
            purchase.id,
        )
        return existing_entitlement, False
    logger.info(
        "Creating entitlement for purchase %s",
        purchase.id,
    )
    entitlement = Entitlement(
        user_id=purchase.user_id,
        purchase_id=purchase.id,
        tier=purchase.tier,
        status="active",
    )

    db.session.add(entitlement)

    purchase.access_status = "granted"

    try:
        db.session.commit()
        logger.info(
            "Provisioning completed successfully for purchase %s",
            purchase.id,
        )  

    except IntegrityError:
        logger.warning(
            "Duplicate entitlement detected for purchase %s",
            purchase.id,
        )
        db.session.rollback()

        existing_entitlement = (
            Entitlement.query.filter_by(
                purchase_id=purchase.id
            ).first()
        )

        if existing_entitlement:
            if purchase.access_status != "granted":
                purchase.access_status = "granted"
                db.session.commit()

                logger.info(
                    "Recovered existing entitlement after IntegrityError for purchase %s",
                    purchase.id,
            )
            return existing_entitlement, False

        logger.exception(
            "Provisioning failed for purchase %s",
            purchase.id,
        )

        raise

    return entitlement, True