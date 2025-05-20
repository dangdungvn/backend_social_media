from django.contrib import admin
from .models import Post, PostMedia, Like, Share


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "created_at",
        "is_public",
        "get_media_count",
        "get_like_count",
    )
    list_filter = ("is_public", "created_at")
    search_fields = ("content", "user__username")
    date_hierarchy = "created_at"

    def get_media_count(self, obj):
        return obj.media.count()

    get_media_count.short_description = "Media"

    def get_like_count(self, obj):
        return obj.likes.count()

    get_like_count.short_description = "Likes"


@admin.register(PostMedia)
class PostMediaAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "media_type", "created_at")
    list_filter = ("media_type", "created_at")


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username",)


@admin.register(Share)
class ShareAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "content")
