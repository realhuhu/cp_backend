from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    phone = models.CharField(max_length=11, null=True, default=None, verbose_name="手机号")
    icon = models.CharField(max_length=32, default="icon/default.jpg", verbose_name="头像")

    def __str__(self):
        return self.username

    class Meta:
        ordering = ["id"]


__all__ = [
    "User",
]
