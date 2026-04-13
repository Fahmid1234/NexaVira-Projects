from django.db import models
from django.contrib.auth.models import User

from clients.models import Client


class Project(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"

    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="projects")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, help_text="Project description and notes")
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    start_date = models.DateField()
    deadline = models.DateField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["deadline", "title"]
        indexes = [
            models.Index(fields=["status", "deadline"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.client.name})"


class ProjectComment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Comment on {self.project.title}"


class ProjectActivity(models.Model):
    class ActivityType(models.TextChoices):
        CREATED = "created", "Created"
        UPDATED = "updated", "Updated"
        STATUS_CHANGED = "status_changed", "Status Changed"
        COMPLETED = "completed", "Completed"
        COMMENTED = "commented", "Commented"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="activities")
    activity_type = models.CharField(max_length=20, choices=ActivityType.choices)
    description = models.CharField(max_length=255)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Project activities"

    def __str__(self) -> str:
        return f"{self.get_activity_type_display()} - {self.project.title}"


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        DEADLINE_APPROACHING = "deadline_approaching", "Deadline Approaching"
        DEADLINE_TODAY = "deadline_today", "Deadline Today"
        OVERDUE = "overdue", "Overdue"
        STATUS_CHANGED = "status_changed", "Status Changed"
        COMMENT_ADDED = "comment_added", "Comment Added"
        PROJECT_CREATED = "project_created", "Project Created"
        PROJECT_UPDATED = "project_updated", "Project Updated"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="notifications")
    notification_type = models.CharField(max_length=30, choices=NotificationType.choices)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.title} - {self.user.username}"
