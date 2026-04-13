from datetime import date
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render
from clients.models import Client
from projects.models import Project, Notification

@login_required
def dashboard_home(request):
    today = date.today()

    total_clients = Client.objects.count()
    total_projects = Project.objects.count()
    active_projects = Project.objects.filter(status=Project.Status.ACTIVE).count()
    completed_projects = Project.objects.filter(status=Project.Status.COMPLETED).count()
    
    projects = (
        Project.objects.select_related("client")
        .all()
        .order_by("deadline", "title")
    )
    sum = 0
    for project in projects:
        p = project.budget
        sum = sum + p

    # Get unread notifications for current user
    unread_notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).select_related('project', 'user').order_by('-created_at')[:5]

    context = {
        "today": today,
        "total_clients": total_clients,
        "total_projects": total_projects,
        "active_projects": active_projects,
        "completed_projects": completed_projects,
        "projects": projects,
        "unread_notifications": unread_notifications,
        "total_budget": sum
    }
    return render(request, "dashboard/home.html", context)

# Create your views here.

