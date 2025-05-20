from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"", views.UserViewSet)
router.register(r"profiles", views.ProfileViewSet)
router.register(r"friendships", views.FriendshipViewSet)
router.register(r"follows", views.FollowViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
