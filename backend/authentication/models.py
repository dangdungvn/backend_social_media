from django.db import models
from django.contrib.auth.models import User


class LoginLog(models.Model):
    """Model để lưu lịch sử đăng nhập của người dùng"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="login_logs")
    login_datetime = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    device_type = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        ordering = ["-login_datetime"]

    def __str__(self):
        return f"{self.user.username} logged in at {self.login_datetime}"
