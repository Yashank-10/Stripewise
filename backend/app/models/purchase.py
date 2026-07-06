import uuid

from app.extensions import db


class Purchase(db.Model):
    __tablename__ = "purchases"

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    user_id = db.Column(
        db.String(36),
        db.ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    stripe_checkout_session_id = db.Column(
        db.String(255),
        unique=True,
        nullable=False
    )

    stripe_customer_id = db.Column(
        db.String(255),
        nullable=True
    )

    stripe_payment_intent_id = db.Column(
        db.String(255),
        nullable=True
    )

    tier = db.Column(
        db.String(50),
        nullable=False
    )

    status = db.Column(
        db.String(50),
        nullable=False,
        default="completed"
    )

    github_access_granted = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    github_invitation_id = db.Column(
        db.String(255),
        nullable=True
    )

    amount = db.Column(
        db.Integer,
        nullable=False
    )

    currency = db.Column(
        db.String(10),
        nullable=False,
        default="usd"
    )

    purchased_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now()
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now()
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now()
    )