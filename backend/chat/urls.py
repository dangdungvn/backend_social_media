from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"rooms", views.ChatRoomViewSet)
router.register(r"messages", views.MessageViewSet)
router.register(r"status", views.UserStatusViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
