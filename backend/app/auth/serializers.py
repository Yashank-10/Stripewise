def serialize_user(user):
    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
    }