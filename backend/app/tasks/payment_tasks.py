from app.celery_app import celery

from app.models.purchase import Purchase
from app.payments.provisioning import provision_purchase


@celery.task(bind=True, max_retries=3)
def provision_purchase_task(self, purchase_id):

    purchase = Purchase.query.get(purchase_id)

    if purchase is None:
        raise ValueError(
            f"Purchase '{purchase_id}' not found."
        )

    entitlement, created = provision_purchase(purchase)

    print("=" * 60)
    print(f"Provisioned Purchase: {purchase.id}")
    print(f"Created New Entitlement: {created}")
    print("=" * 60)

    return {
        "purchase_id": purchase.id,
        "created": created,
    }