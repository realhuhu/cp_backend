from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import *

router = SimpleRouter()
router.register("exercise", ExerciseView, "")
router.register("entry", EntryView, "")
router.register("", CompetitionView, "")
router.register("", CompetitionDetailView, "")

urlpatterns = [
    path("", include(router.urls))
]
