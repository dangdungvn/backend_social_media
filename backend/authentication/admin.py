from django.contrib import admin
from .models import LoginLog


@admin.register(LoginLog)
class LoginLogAdmin(admin.ModelAdmin):
    list_display = ("user", "login_datetime", "ip_address", "device_type")
    list_filter = ("login_datetime", "device_type")
    search_fields = ("user__username", "ip_address")
    date_hierarchy = "login_datetime"
