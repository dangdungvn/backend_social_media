from django.db import models
from django.contrib.auth.models import User


class Room(models.Model):
    """Phòng chat giữa hai người dùng"""

    participants = models.ManyToManyField(User, related_name="chat_rooms")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        usernames = ", ".join([user.username for user in self.participants.all()])
        return f"Chat room: {usernames}"


class Message(models.Model):
    """Tin nhắn trong phòng chat"""

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_messages"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Message by {self.sender.username} in room {self.room.id}"


class MessageMedia(models.Model):
    """Media đính kèm trong tin nhắn"""

    MEDIA_TYPES = (
        ("image", "Image"),
        ("video", "Video"),
        ("file", "File"),
    )

    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="media")
    file = models.FileField(upload_to="chat_media/")
    media_type = models.CharField(max_length=5, choices=MEDIA_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.media_type} in message {self.message.id}"


class UserStatus(models.Model):
    """Trạng thái online của người dùng"""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="chat_status"
    )
    is_online = models.BooleanField(default=False)
    last_activity = models.DateTimeField(auto_now=True)

    def __str__(self):
        status = "online" if self.is_online else "offline"
        return f"{self.user.username} is {status}"
