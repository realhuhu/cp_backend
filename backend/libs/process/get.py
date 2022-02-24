from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler
from django.db.models.query import QuerySet


def getToken(user):
    if isinstance(user, QuerySet):
        user = user.first()
    payload = jwt_payload_handler(user)
    token = jwt_encode_handler(payload)
    return token


def getUserInfo(user):
    return {
        "id": user.id,
        "username": user.username,
        "date_joined": user.date_joined,
        "phone": user.phone,
        "icon": user.icon,
        "is_superuser": user.is_superuser
    }


__all__ = [
    "getToken",
    "getUserInfo",
]
