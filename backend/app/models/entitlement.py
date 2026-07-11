import uuid

from app.extensions import db


class Entitlement(db.Model):
    __tablename__ = "entitlements"

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    user_id = db.Column(
        db.String(36),
        db.ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    purchase_id = db.Column(
        db.String(36),
        db.ForeignKey(
            "purchases.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
    )

    tier = db.Column(
        db.String(50),
        nullable=False,
    )

    status = db.Column(
        db.String(50),
        nullable=False,
        default="active",
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )