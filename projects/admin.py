from django.contrib import admin

from .models import Project, ProjectComment, ProjectActivity, Notification


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "client", "budget", "start_date", "deadline", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("title", "client__name", "description")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Basic Information", {
            "fields": ("title", "description", "client", "status")
        }),
        ("Dates & Budget", {
            "fields": ("start_date", "deadline", "budget")
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


@admin.register(ProjectComment)
class ProjectCommentAdmin(admin.ModelAdmin):
    list_display = ("project", "user", "content_preview", "created_at")
    list_filter = ("created_at",)
    search_fields = ("project__title", "content", "user__username")
    readonly_fields = ("created_at", "updated_at")

    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = "Comment"


@admin.register(ProjectActivity)
class ProjectActivityAdmin(admin.ModelAdmin):
    list_display = ("project", "activity_type", "description", "created_at")
    list_filter = ("activity_type", "created_at")
    search_fields = ("project__title", "description")
    readonly_fields = ("created_at", "details")
    ordering = ("-created_at",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "notification_type", "is_read", "created_at")
    list_filter = ("notification_type", "is_read", "created_at")
    search_fields = ("title", "message", "user__username", "project__title")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
