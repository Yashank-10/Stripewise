from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)

from app.extensions import db
from app.models.user import User


def register_user(email, password, name=None):
    normalized_email = email.strip().lower()

    existing_user = User.query.filter_by(
        email=normalized_email
    ).first()

    if existing_user:
        return None, "Email is already registered"

    password_hash = generate_password_hash(password)

    user = User(
        email=normalized_email,
        password_hash=password_hash,
        name=name,
    )

    db.session.add(user)

    db.session.commit()

    return user, None

def authenticate_user(email, password):
    normalized_email = email.strip().lower()

    user = User.query.filter_by(
        email=normalized_email
    ).first()

    if not user:
        return None

    if not check_password_hash(
        user.password_hash,
        password
    ):
        return None

    return user