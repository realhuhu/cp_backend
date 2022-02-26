from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import *

router = SimpleRouter()
router.register("", SMSCodeView, "code")
router.register("", ImageView, "img")
router.register("", ArticleView, "img")
router.register("articles", ArticleDetailView, "img")
router.register("", SwipeView, "swipe")
router.register("", TopView, "top")

urlpatterns = [
    path("", include(router.urls))
]
