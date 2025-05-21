from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"users", views.UserViewSet, basename="user")
router.register(r"profiles", views.ProfileViewSet, basename="profile")
router.register(r"friendships", views.FriendshipViewSet, basename="friendship")
router.register(r"follows", views.FollowViewSet, basename="follow")

urlpatterns = [
    path("", include(router.urls)),
]
