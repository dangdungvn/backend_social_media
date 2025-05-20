from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return f'Post by {self.user.username} on {self.created_at.strftime("%Y-%m-%d %H:%M")}'

    class Meta:
        ordering = ["-created_at"]


class PostMedia(models.Model):
    MEDIA_TYPES = (
        ("image", "Image"),
        ("video", "Video"),
    )

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="media")
    file = models.FileField(upload_to="post_media/")
    media_type = models.CharField(max_length=5, choices=MEDIA_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.media_type} for post {self.post.id}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")

    def __str__(self):
        return f"{self.user.username} likes post {self.post.id}"


class Share(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shares")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="shares")
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} shared post {self.post.id}"
