from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.entitlement import Entitlement


SUPPORTED_TIERS = {
    "starter",
    "pro",
}


def provision_purchase(purchase):
    if purchase.status != "completed":
        raise ValueError(
            "Cannot provision an incomplete purchase"
        )

    if purchase.tier not in SUPPORTED_TIERS:
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

        return existing_entitlement, False

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

    except IntegrityError:
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

            return existing_entitlement, False

        raise

    return entitlement, True