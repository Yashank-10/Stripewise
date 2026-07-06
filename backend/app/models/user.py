import uuid

from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    purchases = db.relationship(
        "Purchase",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    email = db.Column(
        db.String(255),
        unique=True,
        nullable=False
    )

    email_verified = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    name = db.Column(
        db.String(255),
        nullable=True
    )

    github_username = db.Column(
        db.String(255),
        nullable=True
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