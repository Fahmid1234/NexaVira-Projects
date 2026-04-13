from urllib.parse import quote
from datetime import date, timedelta
from decimal import Decimal
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_POST, require_http_methods
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from accounts.mixins import CeoRequiredMixin

from .forms import ProjectForm
from .models import Project, Notification, ProjectComment


class ProjectListView(CeoRequiredMixin, ListView):
    model = Project
    template_name = "projects/list.html"
    context_object_name = "projects"
    paginate_by = 25

    def get_queryset(self):
        qs = Project.objects.select_related("client").all()

        status = (self.request.GET.get("status") or "").strip().lower()
        if status in (Project.Status.ACTIVE, Project.Status.COMPLETED):
            qs = qs.filter(status=status)

        q = (self.request.GET.get("q") or "").strip()
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(client__name__icontains=q))

        sort = (self.request.GET.get("sort") or "").strip().lower()
        if sort == "deadline":
            qs = qs.order_by("deadline", "title")
        elif sort == "-deadline":
            qs = qs.order_by("-deadline", "title")
        elif sort == "budget":
            qs = qs.order_by("budget", "deadline")
        elif sort == "-budget":
            qs = qs.order_by("-budget", "deadline")
        else:
            qs = qs.order_by("deadline", "title")

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["status_filter"] = (self.request.GET.get("status") or "").strip().lower()
        ctx["q"] = (self.request.GET.get("q") or "").strip()
        ctx["sort"] = (self.request.GET.get("sort") or "").strip().lower()
        return ctx


class ProjectCreateView(CeoRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/form.html"
    success_url = reverse_lazy("projects:list")

    def form_valid(self, form):
        response = super().form_valid(form)
        Notification.objects.create(
            user=self.request.user,
            project=self.object,
            notification_type=Notification.NotificationType.PROJECT_CREATED,
            title=f"Project created: {self.object.title}",
            message=f"Project '{self.object.title}' for {self.object.client.name} was created."
        )
        messages.success(self.request, "Project created.")
        return response


class ProjectUpdateView(CeoRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/form.html"
    success_url = reverse_lazy("projects:list")

    def form_valid(self, form):
        response = super().form_valid(form)
        Notification.objects.create(
            user=self.request.user,
            project=self.object,
            notification_type=Notification.NotificationType.PROJECT_UPDATED,
            title=f"Project updated: {self.object.title}",
            message=f"Project '{self.object.title}' was updated."
        )
        messages.success(self.request, "Project updated.")
        return response


class ProjectDeleteView(CeoRequiredMixin, DeleteView):
    model = Project
    template_name = "projects/confirm_delete.html"
    success_url = reverse_lazy("projects:list")

    def form_valid(self, form):
        messages.success(self.request, "Project deleted.")
        return super().form_valid(form)


@require_POST
def mark_completed(request, pk: int):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("accounts:login")
    project = get_object_or_404(Project, pk=pk)
    project.status = Project.Status.COMPLETED
    project.save(update_fields=["status", "updated_at"])
    messages.success(request, "Project marked as completed.")
    return redirect(request.POST.get("next") or "projects:list")


@login_required
@require_http_methods(["POST"])
def bulk_action(request):
    """Handle bulk actions on selected projects"""
    action = request.POST.get('action')
    project_ids = request.POST.getlist('project_ids')
    
    if not project_ids:
        messages.error(request, "Please select at least one project.")
        return redirect('projects:list')
    
    projects = Project.objects.filter(id__in=project_ids)
    
    if action == 'delete':
        count = projects.count()
        projects.delete()
        messages.success(request, f"Deleted {count} project(s).")
    
    elif action == 'complete':
        count = projects.update(status=Project.Status.COMPLETED)
        messages.success(request, f"Marked {count} project(s) as completed.")
    
    elif action == 'activate':
        count = projects.update(status=Project.Status.ACTIVE)
        messages.success(request, f"Marked {count} project(s) as active.")
    
    return redirect('projects:list')


@login_required
def export_pdf(request, pk: int):
    """Export single project as PDF"""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from datetime import datetime
    except ImportError:
        messages.error(request, "PDF export requires reportlab. Install it with: pip install reportlab")
        return redirect('projects:list')
    
    project = get_object_or_404(Project, pk=pk)
    
    # Create PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="project_{project.id}_{date.today()}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=30,
    )
    elements.append(Paragraph(f"Project Report", title_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    # Project details table
    data = [
        ['Project Title', project.title],
        ['Client', project.client.name],
        ['Status', project.get_status_display()],
        ['Budget', f"৳ {project.budget:,.2f}"],
        ['Start Date', project.start_date.strftime('%B %d, %Y')],
        ['Deadline', project.deadline.strftime('%B %d, %Y')],
        ['Days Remaining', str(max(0, (project.deadline - date.today()).days))],
        ['Created', project.created_at.strftime('%B %d, %Y %I:%M %p')],
    ]
    
    table = Table(data, colWidths=[2 * inch, 3 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.3 * inch))
    
    # Description
    if project.description:
        elements.append(Paragraph("Description", styles['Heading2']))
        elements.append(Paragraph(project.description, styles['Normal']))
        elements.append(Spacer(1, 0.2 * inch))
    
    # Comments
    if project.comments.exists():
        elements.append(Paragraph("Comments", styles['Heading2']))
        for comment in project.comments.all()[:10]:
            comment_text = f"<b>{comment.user.username if comment.user else 'Anonymous'}</b> ({comment.created_at.strftime('%B %d, %Y')})"
            elements.append(Paragraph(comment_text, styles['Normal']))
            elements.append(Paragraph(comment.content, styles['Normal']))
            elements.append(Spacer(1, 0.1 * inch))
    
    # Build PDF
    doc.build(elements)
    return response


@login_required
@require_POST
def add_comment(request, pk: int):
    """Add comment to a project"""
    project = get_object_or_404(Project, pk=pk)
    content = request.POST.get('content', '').strip()
    
    if not content:
        messages.error(request, "Comment cannot be empty.")
    else:
        comment = ProjectComment.objects.create(
            project=project,
            user=request.user,
            content=content
        )
        
        # Create notification for comment
        Notification.objects.create(
            user=request.user,
            project=project,
            notification_type=Notification.NotificationType.COMMENT_ADDED,
            title=f"You commented on {project.title}",
            message=content[:100]
        )
        
        messages.success(request, "Comment added successfully.")
    
    return redirect('projects:edit', pk=pk)


@login_required
def get_project_comments(request, pk: int):
    """API endpoint to get project comments"""
    project = get_object_or_404(Project, pk=pk)
    comments = project.comments.select_related('user').order_by('-created_at')
    
    comments_data = [
        {
            'id': comment.id,
            'user': comment.user.username,
            'user_id': comment.user.id,
            'user_full': comment.user.get_full_name() or comment.user.username,
            'content': comment.content,
            'created_at': comment.created_at.isoformat(),
            'created_at_display': comment.created_at.strftime('%b %d, %Y at %I:%M %p'),
            'updated_at': comment.updated_at.isoformat(),
            'is_edited': (comment.updated_at - comment.created_at).total_seconds() > 1,
            'is_owner': comment.user == request.user,
        }
        for comment in comments
    ]
    
    return JsonResponse({'comments': comments_data})


@login_required
def edit_comment(request, pk: int, comment_id: int):
    """Edit a project comment"""
    project = get_object_or_404(Project, pk=pk)
    comment = get_object_or_404(ProjectComment, pk=comment_id, project=project)
    
    # Only allow comment author to edit
    if comment.user != request.user:
        return JsonResponse({'error': 'You can only edit your own comments'}, status=403)
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if not content:
            return JsonResponse({'error': 'Comment cannot be empty'}, status=400)
        
        comment.content = content
        comment.save(update_fields=['content', 'updated_at'])
        
        return JsonResponse({
            'success': True,
            'comment': {
                'id': comment.id,
                'content': comment.content,
                'updated_at': comment.updated_at.isoformat(),
                'is_edited': True,
            }
        })
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def delete_comment(request, pk: int, comment_id: int):
    """Delete a project comment"""
    project = get_object_or_404(Project, pk=pk)
    comment = get_object_or_404(ProjectComment, pk=comment_id, project=project)
    
    # Only allow comment author or project owner to delete
    if comment.user != request.user and request.user != project.client.owner if hasattr(project.client, 'owner') else False:
        return JsonResponse({'error': 'You can only delete your own comments'}, status=403)
    
    if request.method == 'POST':
        comment_id = comment.id
        comment.delete()
        return JsonResponse({'success': True, 'comment_id': comment_id})
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def notifications_page(request):
    """Display notifications page"""
    notifications = Notification.objects.filter(user=request.user).select_related('project').order_by('-created_at')
    return render(request, 'projects/notifications.html', {'notifications': notifications})


@login_required
def notifications_api(request):
    """API endpoint for notifications"""
    notifications = Notification.objects.filter(user=request.user).select_related('project').order_by('-created_at')[:50]
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    notifications_payload = [
        {
            'id': n.id,
            'project_id': n.project.id,
            'project_title': n.project.title,
            'notification_type': n.notification_type,
            'title': n.title,
            'message': n.message,
            'is_read': n.is_read,
            'created_at': n.created_at.isoformat(),
        }
        for n in notifications
    ]

    return JsonResponse({'notifications': notifications_payload, 'unread_count': unread_count})


@login_required
@require_POST
def mark_notification_read(request, pk: int):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save(update_fields=['is_read'])
    return JsonResponse({'success': True})


@login_required
@require_POST
def mark_all_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'success': True})


