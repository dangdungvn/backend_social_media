from django.db import models
from django.contrib.auth.models import User
from posts.models import Post


class Comment(models.Model):
    VERIFICATION_STATUS = (
        ("unverified", "Chưa xác minh"),
        ("correct", "Đúng"),
        ("incorrect", "Sai"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    verification_status = models.CharField(
        max_length=10, choices=VERIFICATION_STATUS, default="unverified"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.user.username} on post {self.post.id}"

    @property
    def is_reply(self):
        return self.parent is not None

    @property
    def vote_score(self):
        upvotes = self.votes.filter(vote_type="upvote").count()
        downvotes = self.votes.filter(vote_type="downvote").count()
        return upvotes - downvotes


class CommentVote(models.Model):
    VOTE_TYPES = (
        ("upvote", "Upvote"),
        ("downvote", "Downvote"),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comment_votes"
    )
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="votes")
    vote_type = models.CharField(max_length=8, choices=VOTE_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "comment")

    def __str__(self):
        return f"{self.user.username} {self.vote_type}d comment {self.comment.id}"
