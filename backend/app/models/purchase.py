import uuid

from app.extensions import db


class Purchase(db.Model):
    __tablename__ = "purchases"

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

    checkout_session_id = db.Column(
        db.String(255),
        unique=True,
        nullable=False,
    )

    tier = db.Column(
        db.String(50),
        nullable=False,
    )

    amount = db.Column(
        db.Integer,
        nullable=False,
    )

    currency = db.Column(
        db.String(10),
        nullable=False,
    )

    status = db.Column(
        db.String(50),
        nullable=False,
        default="completed",
    )

    access_status = db.Column(
        db.String(50),
        nullable=False,
        default="pending",
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