from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "theme", "notifications_enabled", "email_notifications", "created_at")
    list_filter = ("theme", "notifications_enabled", "email_notifications")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("created_at", "updated_at")
