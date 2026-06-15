from uuid import uuid4

from app.models.user import User
from app.core.security import hash_password


def create_user(db, user_data):

    user = User(
        id=str(uuid4()),
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(
            user_data.password
        ),
        role=user_data.role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user