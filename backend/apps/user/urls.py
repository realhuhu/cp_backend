from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import *

router = SimpleRouter()
router.register("", LoginView, "login")
router.register("", UserInfoView, "user_info")

urlpatterns = [
    path("", include(router.urls))
]
