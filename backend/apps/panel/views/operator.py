"""
Operator views — sees assigned tasks, uploads documents.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from ..forms import DocumentUploadForm


@method_decorator(login_required(login_url='/'), name='dispatch')
class OperatorHomeView(View):
    """Operator main view — tasks assigned to them."""

    def get(self, request):
        user = request.user
        if not hasattr(user, 'profile') or user.profile.role.name != 'operator':
            messages.error(request, _('No tenés acceso.'))
            return redirect('landing:home')

        from apps.tasks.models import Task
        tasks = Task.objects.filter(assigned_to=user).select_related('created_by')

        return render(request, 'panel/operator/home.html', {
            'tasks': tasks,
            'pending_count': tasks.filter(status='pending').count(),
            'in_progress_count': tasks.filter(status='in_progress').count(),
            'completed_count': tasks.filter(status='completed').count(),
        })


@method_decorator(login_required(login_url='/'), name='dispatch')
class OperatorTaskDetailView(View):
    """View and update a task."""

    def get(self, request, pk):
        from apps.tasks.models import Task
        user = request.user
        if not hasattr(user, 'profile') or user.profile.role.name != 'operator':
            messages.error(request, _('No tenés acceso.'))
            return redirect('landing:home')

        task = get_object_or_404(Task, pk=pk, assigned_to=user)
        return render(request, 'panel/operator/task_detail.html', {
            'task': task,
        })

    def post(self, request, pk):
        from apps.tasks.models import Task
        user = request.user
        # Re-check the operator role — this is a state-mutating endpoint and
        # must not be reachable by other roles even if they are assigned to the
        # task. The GET branch checks it; the POST must too.
        if not hasattr(user, 'profile') or user.profile.role.name != 'operator':
            messages.error(request, _('No tenés acceso.'))
            return redirect('landing:home')

        task = get_object_or_404(Task, pk=pk, assigned_to=user)

        new_status = request.POST.get('status')
        if new_status in dict(Task.STATUS_CHOICES):
            task.status = new_status
            if new_status == 'completed':
                from django.utils import timezone
                task.completed_at = timezone.now()
            else:
                # Leaving the completed state clears the stale completion
                # timestamp so it cannot report a wrong completion date.
                task.completed_at = None
            task.save()
            messages.success(request, _('Tarea actualizada.'))
        return redirect('panel:operator_task_detail', pk=pk)


@method_decorator(login_required(login_url='/'), name='dispatch')
class OperatorDocumentUploadView(View):
    """Upload documents (operator)."""

    def get(self, request):
        user = request.user
        if not hasattr(user, 'profile') or user.profile.role.name != 'operator':
            messages.error(request, _('No tenés acceso.'))
            return redirect('landing:home')

        form = DocumentUploadForm()
        return render(request, 'panel/operator/document_upload.html', {
            'form': form,
        })

    def post(self, request):
        user = request.user
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.owner = user
            doc.save()
            messages.success(request, _('Documento subido.'))
            return redirect('panel:operator_home')
        return render(request, 'panel/operator/document_upload.html', {
            'form': form,
        })
