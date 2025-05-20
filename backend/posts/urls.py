from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"", views.PostViewSet)
router.register(r"media", views.PostMediaViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
