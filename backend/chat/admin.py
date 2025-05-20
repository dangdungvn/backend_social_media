from django.contrib import admin
from .models import Room, Message, MessageMedia, UserStatus


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("id", "get_participants", "created_at", "updated_at")
    list_filter = ("created_at",)
    search_fields = ("participants__username",)
    date_hierarchy = "created_at"

    def get_participants(self, obj):
        return ", ".join([user.username for user in obj.participants.all()])

    get_participants.short_description = "Participants"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "room", "sender", "created_at", "is_read")
    list_filter = ("is_read", "created_at")
    search_fields = ("content", "sender__username")
    date_hierarchy = "created_at"


@admin.register(MessageMedia)
class MessageMediaAdmin(admin.ModelAdmin):
    list_display = ("id", "message", "media_type", "created_at")
    list_filter = ("media_type", "created_at")


@admin.register(UserStatus)
class UserStatusAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "is_online", "last_activity")
    list_filter = ("is_online",)
    search_fields = ("user__username",)
