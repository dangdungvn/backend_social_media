from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    cover_photo = models.ImageField(upload_to="covers/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"


class Friendship(models.Model):
    STATUS_CHOICES = (
        ("pending", "Đang chờ"),
        ("accepted", "Đã chấp nhận"),
        ("rejected", "Đã từ chối"),
    )

    sender = models.ForeignKey(
        User, related_name="sent_friendship_requests", on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        User, related_name="received_friendship_requests", on_delete=models.CASCADE
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("sender", "receiver")

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}: {self.status}"


class Follow(models.Model):
    follower = models.ForeignKey(
        User, related_name="following", on_delete=models.CASCADE
    )
    followed = models.ForeignKey(
        User, related_name="followers", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "followed")

    def __str__(self):
        return f"{self.follower.username} follows {self.followed.username}"


# Signals để tự động tạo profile khi tạo user mới
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Kiểm tra xem user có profile chưa, nếu chưa thì tạo mới
    try:
        instance.profile.save()
    except User.profile.RelatedObjectDoesNotExist:
        # Use get_or_create to prevent race conditions
        profile, created = Profile.objects.get_or_create(user=instance)
        if created:
            print(f"Created missing profile for {instance.username}")
