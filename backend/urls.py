from django.urls import path, include

urlpatterns = [
    path("common/", include("common.urls")),
    path("user/", include("user.urls")),
    path("admin/", include("admin.urls")),
    path("competition/", include("competition.urls"))
]
