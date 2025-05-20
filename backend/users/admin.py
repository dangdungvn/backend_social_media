from django.contrib import admin
from .models import Profile, Friendship, Follow


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "location", "birth_date", "created_at")
    search_fields = ("user__username", "location")
    list_filter = ("created_at",)


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ("sender", "receiver", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("sender__username", "receiver__username")


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("follower", "followed", "created_at")
    list_filter = ("created_at",)
    search_fields = ("follower__username", "followed__username")
