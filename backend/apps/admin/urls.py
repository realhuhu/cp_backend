from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import *

router = SimpleRouter()
router.register("question-bank", QuestionBankView, "")
router.register("competition", CompetitionView, "")
router.register("user", UserView, "")

urlpatterns = [
    path("", include(router.urls))
]
