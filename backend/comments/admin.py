from django.contrib import admin
from .models import Comment, CommentVote


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "post",
        "parent",
        "created_at",
        "verification_status",
        "get_vote_score",
    )
    list_filter = ("verification_status", "created_at")
    search_fields = ("content", "user__username")
    date_hierarchy = "created_at"

    def get_vote_score(self, obj):
        return obj.vote_score

    get_vote_score.short_description = "Vote Score"


@admin.register(CommentVote)
class CommentVoteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "comment", "vote_type", "created_at")
    list_filter = ("vote_type", "created_at")
    search_fields = ("user__username",)
