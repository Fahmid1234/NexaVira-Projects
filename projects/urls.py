from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    path("", views.ProjectListView.as_view(), name="list"),
    path("new/", views.ProjectCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", views.ProjectUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.ProjectDeleteView.as_view(), name="delete"),
    path("<int:pk>/complete/", views.mark_completed, name="complete"),
    path("bulk-action/", views.bulk_action, name="bulk_action"),
    path("<int:pk>/export/", views.export_pdf, name="export"),
    path("<int:pk>/comment/", views.add_comment, name="add_comment"),
    path("<int:pk>/comments/<int:comment_id>/edit/", views.edit_comment, name="edit_comment"),
    path("<int:pk>/comments/<int:comment_id>/delete/", views.delete_comment, name="delete_comment"),
    path("api/<int:pk>/comments/", views.get_project_comments, name="api_comments"),
    path("notifications/", views.notifications_page, name="notifications"),
    path("api/notifications/", views.notifications_api, name="api_notifications"),
    path("api/notifications/<int:pk>/read/", views.mark_notification_read, name="api_notification_read"),
    path("api/notifications/read-all/", views.mark_all_notifications_read, name="api_notifications_read_all"),
]

