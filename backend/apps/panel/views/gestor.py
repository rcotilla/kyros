"""
Gestor views — manages clients, processes, documents, and templates.

Split by domain:
  - Dashboard
  - Clients (CRUD)
  - Processes (CRUD + step management)
  - Documents (list + upload + generation)
  - Templates (CRUD + step management)
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django import forms
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.db.models import Q, F, Max
from django.utils.translation import gettext_lazy as _

from apps.clients.models import Client
from apps.processes.models import (
    Process, ProcessStep, ProcessTemplate, ProcessTemplateStep,
)
from apps.documents.models import Document

from ..forms import (
    ClientForm, ProcessForm, ProcessStepForm,
    DocumentUploadForm, ProcessFilterForm,
    ProcessTemplateForm, ProcessTemplateStepForm,
)
from .common import GestorRequiredMixin


# ============================================================
# DASHBOARD
# ============================================================

@method_decorator(login_required(login_url='/'), name='dispatch')
class GestorHomeView(GestorRequiredMixin, View):
    """Gestor main view — overview of clients and processes."""

    def get(self, request):
        user = request.user
        if hasattr(user, 'profile') and user.profile.role.name == 'admin':
            clients = Client.objects.filter(status='active')
            processes = Process.objects.all()
        else:
            clients = Client.objects.filter(
                Q(assigned_to=user) | Q(created_by=user), status='active'
            ).distinct()
            processes = Process.objects.filter(
                Q(gestor=user) | Q(client__assigned_to=user)
            ).distinct()

        context = {
            'total_clients': clients.count(),
            'active_clients': clients.filter(status='active').count(),
            'total_processes': processes.count(),
            'processes_by_status': {
                s[0]: processes.filter(status=s[0]).count()
                for s in Process.STATUS_CHOICES
            },
            'recent_processes': processes.select_related(
                'client', 'process_type'
            )[:5],
            'recent_clients': clients[:5],
        }
        return render(request, 'panel/gestor/home.html', context)


# ============================================================
# CLIENTS
# ============================================================

@method_decorator(login_required(login_url='/'), name='dispatch')
class GestorClientListView(GestorRequiredMixin, View):
    """List all clients."""

    def get(self, request):
        user = request.user
        search = request.GET.get('search', '')

        if hasattr(user, 'profile') and user.profile.role.name == 'admin':
            qs = Client.objects.filter(status='active')
        else:
            qs = Client.objects.filter(
                Q(assigned_to=user) | Q(created_by=user), status='active'
            ).distinct()

        if search:
            qs = qs.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(document_number__icontains=search) |
                Q(email__icontains=search)
            )

        return render(request, 'panel/gestor/client_list.html', {
            'clients': qs,
            'search': search,
            'total': qs.count(),
        })


@method_decorator(login_required(login_url='/'), name='dispatch')
class GestorClientCreateView(GestorRequiredMixin, View):
    """Create a new client."""

    def get(self, request):
        form = ClientForm()
        return render(request, 'panel/gestor/client_form.html', {
            'form': form,
            'title': 'Nuevo Cliente',
        })

    def post(self, request):
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.created_by = request.user
            client.save()
            messages.success(request, _(f'Cliente "{client.full_name}" creado correctamente.'))
            return redirect('panel:gestor_clients')
        return render(request, 'panel/gestor/client_form.html', {
            'form': form,
            'title': 'Nuevo Cliente',
        })


@method_decorator(login_required(login_url='/'), name='dispatch')
class GestorClientDetailView(GestorRequiredMixin, View):
    """View client details + their processes."""

    def get(self, request, pk):
        client = get_object_or_404(Client, pk=pk)
        processes = client.processes.select_related('process_type').order_by('-created_at')
        documents = client.documents.all()

        return render(request, 'panel/gestor/client_detail.html', {
            'client': client,
            'processes': processes,
            'documents': documents,
        })


@method_decorator(login_required(login_url='/'), name='dispatch')
class GestorClientEditView(GestorRequiredMixin, View):
    """Edit a client."""

    def get(self, request, pk):
        client = get_object_or_404(Client, pk=pk)
        form = ClientForm(instance=client)
        return render(request, 'panel/gestor/client_form.html', {
            'form': form,
            'title': f'Editar: {client.full_name}',
            'client': client,
        })

    def post(self, request, pk):
        client = get_object_or_404(Client, pk=pk)

        # Desactivar: solo cambia el estado y redirige a la lista
        if request.POST.get('action') == 'deactivate':
            client.status = 'inactive'
            client.save()
            messages.success(request, _('Cliente "%s" desactivado.') % client.full_name)
            return redirect('panel:gestor_clients')

        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, _('Cliente actualizado correctamente.'))
            return redirect('panel:gestor_client_detail', pk=pk)
        return render(request, 'panel/gestor/client_form.html', {
            'form': form,
            'title': f'Editar: {client.full_name}',
            'client': client,
        })


# ============================================================
# PROCESSES
# ============================================================

@method_decorator(login_required(login_url='/'), name='dispatch')
class GestorProcessListView(GestorRequiredMixin, View):
    """List processes with filters."""

    def get(self, request):
        user = request.user
        filter_form = ProcessFilterForm(request.GET)
        search = request.GET.get('search', '')
        status = request.GET.get('status', '')
        priority = request.GET.get('priority', '')

        if hasattr(user, 'profile') and user.profile.role.name == 'admin':
            qs = Process.objects.select_related('client', 'process_type', 'gestor')
        else:
            qs = Process.objects.select_related(
                'client', 'process_type', 'gestor'
            ).filter(
                Q(gestor=user) | Q(client__assigned_to=user)
            ).distinct()

        if search:
            qs = qs.filter(
                Q(file_number__icontains=search) |
                Q(title__icontains=search) |
                Q(client__first_name__icontains=search) |
                Q(client__last_name__icontains=search)
            )
        if status:
            qs = qs.filter(status=status)
        if priority:
            qs = qs.filter(priority=priority)

        return render(request, 'panel/gestor/process_list.html', {
            'processes': qs,
            'filter_form': filter_form,
            'total': qs.count(),
        })


@method_decorator(login_required(login_url='/'), name='dispatch')
class GestorProcessCreateView(GestorRequiredMixin, View):
    """Create a new process, optionally from a template."""

    def get(self, request):
        form = ProcessForm()
        client_id = request.GET.get('client')
        if client_id:
            form.fields['client'].initial = client_id
        return render(request, 'panel/gestor/process_form.html', {
            'form': form,
            'title': 'Nuevo Proceso',
        })

    def post(self, request):
        form = ProcessForm(request.POST)
        if form.is_valid():
            process = form.save(commit=False)
            process.created_by = request.user
            if not process.gestor:
                process.gestor = request.user
            process.save()

            template = form.cleaned_data.get('template')
            if template:
                steps_created = template.apply_to(process)
                messages.success(
                    request,
                    _(f'Proceso "{process.file_number}" creado con {steps_created} pasos de la plantilla "{template.name}".')
                )
            else:
                messages.success(request, _(f'Proceso "{process.file_number}" creado.'))

            return redirect('panel:gestor_process_detail', pk=process.pk)
        return render(request, 'panel/gestor/process_form.html', {
            'form': form,
            'title': 'Nuevo Proceso',
        })


@method_decorator(login_required(login_url='/'), name='dispatch')
class GestorProcessDetailView(GestorRequiredMixin, View):
    """View process details + steps + documents."""

    def get(self, request, pk):
        process = get_object_or_404(
            Process.objects.select_related('client', 'process_type', 'gestor', 'operator'),
            pk=pk
        )
        steps = process.steps.all().order_by('order')
        documents = process.documents.all()
        step_form = ProcessStepForm()

        return render(request, 'panel/gestor/process_detail.html', {
            'process': process,
            'steps': steps,
            'documents': documents,
            'step_form': step_form,
            'step_status_choices': ProcessStep.STATUS_CHOICES,
        })


@method_decorator(login_required(login_url='/'), name='dispatch')
class GestorProcessEditView(GestorRequiredMixin, View):
    """Edit a process."""

    def get(self, request, pk):
        process = get_object_or_404(Process, pk=pk)
        form = ProcessForm(instance=process)
        return render(request, 'panel/gestor/process_form.html', {
            'form': form,
            'title': f'Editar: {process.file_number}',
            'process': process,
        })

    def post(self, request, pk):
        process = get_object_or_404(Process, pk=pk)
        form = ProcessForm(request.POST, instance=process)
        if form.is_valid():
            form.save()
            messages.success(request, _('Proceso actualizado.'))
            return redirect('panel:gestor_process_detail', pk=pk)
        return render(request, 'panel/gestor/process_form.html', {
            'form': form,
            'title': f'Editar: {process.file_number}',
            'process': process,
        })


@method_decorator(login_required(login_url='/'), name='dispatch')
class GestorProcessDeleteView(GestorRequiredMixin, View):
    """Delete a process."""

    def post(self, request, pk):
        process = get_object_or_404(Process, pk=pk)
        file_number = process.file_number
        ProcessStep.objects.filter(process=process).delete()
        process.delete()
        messages.success(request, _('Proceso "%s" eliminado.') % file_number)
        return redirect('panel:gestor_processes')


# --- Process Steps ---

@method_decorator(login_required(login_url='/'), name='dispatch')
class GestorProcessAddStepView(GestorRequiredMixin, View):
    """Add a step to a process."""

    def post(self, request, pk):
        process = get_object_or_404(Process, pk=pk)
        form = ProcessStepForm(request.POST)
        if form.is_valid():
            raw_order = request.POST.get('order', '').strip()
            try:
                new_order = int(raw_order) if raw_order else 0
            except (ValueError, TypeError):
                new_order = 0
            if new_order < 1:
                max_order = ProcessStep.objects.filter(
                    process=process
                ).aggregate(Max('order'))['order__max'] or 0
                new_order = max_order + 1
            else:
                ProcessStep.objects.filter(
                    process=process, order__gte=new_order
                ).update(order=F('order') + 1)
            step = form.save(commit=False)
            step.process = process
            step.order = new_order
            step.save()
            messages.success(request, _('Paso agregado al proceso.'))
        return redirect('panel:gestor_process_detail', pk=pk)


@method_decorator(login_required(login_url='/'), name='dispatch')
class GestorProcessUpdateStepView(GestorRequiredMixin, View):
    """Update the status of a single step within a process."""

    def post(self, request, process_pk, step_pk):
        process = get_object_or_404(Process, pk=process_pk)
        step = get_object_or_404(ProcessStep, pk=step_pk, process=process)
        new_status = request.POST.get('status', '').strip()
        valid_statuses = [c[0] for c in ProcessStep.STATUS_CHOICES]
        if new_status in valid_statuses:
            step.status = new_status
            step.save()
            messages.success(request, _('Paso "%s" actualizado a "%s".') % (step.name, step.get_status_display()))
        else:
            messages.error(request, _('Estado no válido.'))
        return redirect('panel:gestor_process_detail', pk=process_pk)


@method_decorator(login_required(login_url='/'), name='dispatch')
class GestorProcessDeleteStepView(GestorRequiredMixin, View):
    """Delete a step from a process."""

    def post(self, request, process_pk, step_pk):
        process = get_object_or_404(Process, pk=process_pk)
        step = get_object_or_404(ProcessStep, pk=step_pk, process=process)
        deleted_order = step.order
        step_name = step.name
        step.delete()
        ProcessStep.objects.filter(
            process=process, order__gt=deleted_order
        ).update(order=F('order') - 1)
        messages.success(request, _('Paso "%s" eliminado.') % step_name)
        return redirect('panel:gestor_process_detail', pk=process_pk)


@method_decorator(login_required(login_url='/'), name='dispatch')
class GestorProcessStepsUpdateView(GestorRequiredMixin, View):
    """Batch update all steps: status changes + deletions in one form."""

    def post(self, request, pk):
        process = get_object_or_404(Process, pk=pk)
        valid_statuses = [c[0] for c in ProcessStep.STATUS_CHOICES]
        updated = 0
        deleted = 0

        for key, value in request.POST.items():
            if key.startswith('status_'):
                step_id = key.replace('status_', '')
                try:
                    step = ProcessStep.objects.get(pk=step_id, process=process)
                    if value in valid_statuses and step.status != value:
                        step.status = value
                        step.save()
                        updated += 1
                except ProcessStep.DoesNotExist:
                    continue

        delete_ids = request.POST.getlist('delete')
        if delete_ids:
            steps_to_delete = ProcessStep.objects.filter(
                pk__in=delete_ids, process=process
            )
            for step in steps_to_delete:
                deleted_order = step.order
                step.delete()
                ProcessStep.objects.filter(
                    process=process, order__gt=deleted_order
                ).update(order=F('order') - 1)
                deleted += 1

        if updated or deleted:
            parts = []
            if updated:
                parts.append(_('%d paso(s) actualizado(s)') % updated)
            if deleted:
                parts.append(_('%d paso(s) eliminado(s)') % deleted)
            messages.success(request, ', '.join(parts) + '.')
        else:
            messages.info(request, _('Sin cambios.'))

        return redirect('panel:gestor_process_detail', pk=pk)


# ============================================================
# DOCUMENTS
# ============================================================

@method_decorator(login_required(login_url='/'), name='dispatch')
class GestorDocumentListView(GestorRequiredMixin, View):
    """List documents."""

    def get(self, request):
        user = request.user
        search = request.GET.get('search', '')

        if hasattr(user, 'profile') and user.profile.role.name == 'admin':
            qs = Document.objects.select_related('owner', 'client', 'process')
        else:
            qs = Document.objects.select_related(
                'owner', 'client', 'process'
            ).filter(
                Q(owner=user) | Q(client__assigned_to=user) | Q(process__gestor=user)
            ).distinct()

        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(client__first_name__icontains=search) |
                Q(process__file_number__icontains=search)
            )

        return render(request, 'panel/gestor/document_list.html', {
            'documents': qs,
            'search': search,
            'total': qs.count(),
        })


@method_decorator(login_required(login_url='/'), name='dispatch')
class GestorDocumentUploadView(GestorRequiredMixin, View):
    """Upload a document."""

    def get(self, request):
        form = DocumentUploadForm()
        client_id = request.GET.get('client')
        process_id = request.GET.get('process')

        # Contextual upload: linked to a specific process
        process = None
        if process_id:
            process = get_object_or_404(Process, pk=process_id)
            form.fields['client'].initial = process.client_id
            form.fields['process'].initial = process.pk
            form.fields['client'].widget = forms.HiddenInput()
            form.fields['process'].widget = forms.HiddenInput()

        if client_id and not process:
            form.fields['client'].initial = client_id

        return render(request, 'panel/gestor/document_upload.html', {
            'form': form,
            'title': 'Subir Documento',
            'process': process,
        })

    def post(self, request):
        form = DocumentUploadForm(request.POST, request.FILES)
        process_id = request.POST.get('process')

        # Hide fields on re-render if contextual
        process = None
        if process_id:
            process = get_object_or_404(Process, pk=process_id)
            form.fields['client'].widget = forms.HiddenInput()
            form.fields['process'].widget = forms.HiddenInput()

        if form.is_valid():
            doc = form.save(commit=False)
            doc.owner = request.user
            doc.save()
            messages.success(request, _(f'Documento "{doc.title}" subido.'))
            if process:
                return redirect('panel:gestor_process_detail', pk=process.pk)
            return redirect('panel:gestor_documents')
        return render(request, 'panel/gestor/document_upload.html', {
            'form': form,
            'title': 'Subir Documento',
            'process': process,
        })


@method_decorator(login_required(login_url='/'), name='dispatch')
class GestorDocumentDeleteView(GestorRequiredMixin, View):
    """Delete a document with confirmation."""

    def post(self, request, pk):
        doc = get_object_or_404(Document, pk=pk)
        process_pk = doc.process_id
        doc_title = doc.title
        doc.file.delete(save=False)
        doc.delete()
        messages.success(request, _(f'Documento "{doc_title}" eliminado.'))
        if process_pk:
            return redirect('panel:gestor_process_detail', pk=process_pk)
        return redirect('panel:gestor_documents')


@method_decorator(login_required(login_url='/'), name='dispatch')
class GestorDocumentGenerationView(GestorRequiredMixin, View):
    """Document generation hub — contracts, letters, and similar documents."""

    def get(self, request):
        return render(request, 'panel/gestor/document_generation.html')


# ============================================================
# PROCESS TEMPLATES
# ============================================================

@method_decorator(login_required(login_url='/'), name='dispatch')
class GestorTemplateListView(GestorRequiredMixin, View):
    """List process templates."""

    def get(self, request):
        templates = ProcessTemplate.objects.select_related('process_type').prefetch_related('template_steps')
        return render(request, 'panel/gestor/template_list.html', {
            'templates': templates,
            'total': templates.count(),
        })


@method_decorator(login_required(login_url='/'), name='dispatch')
class GestorTemplateCreateView(GestorRequiredMixin, View):
    """Create a new process template."""

    def get(self, request):
        form = ProcessTemplateForm()
        return render(request, 'panel/gestor/template_form.html', {
            'form': form,
            'title': 'Nueva Plantilla',
        })

    def post(self, request):
        form = ProcessTemplateForm(request.POST)
        if form.is_valid():
            template = form.save(commit=False)
            template.created_by = request.user
            template.save()
            messages.success(request, _(f'Plantilla "{template.name}" creada.'))
            return redirect('panel:gestor_template_detail', pk=template.pk)
        return render(request, 'panel/gestor/template_form.html', {
            'form': form,
            'title': 'Nueva Plantilla',
        })


@method_decorator(login_required(login_url='/'), name='dispatch')
class GestorTemplateDetailView(GestorRequiredMixin, View):
    """View template details + steps."""

    def get(self, request, pk):
        template = get_object_or_404(
            ProcessTemplate.objects.select_related('process_type'),
            pk=pk
        )
        steps = template.template_steps.all()
        step_form = ProcessTemplateStepForm()

        return render(request, 'panel/gestor/template_detail.html', {
            'template': template,
            'steps': steps,
            'step_form': step_form,
        })


@method_decorator(login_required(login_url='/'), name='dispatch')
class GestorTemplateEditView(GestorRequiredMixin, View):
    """Edit a process template."""

    def get(self, request, pk):
        template = get_object_or_404(ProcessTemplate, pk=pk)
        form = ProcessTemplateForm(instance=template)
        return render(request, 'panel/gestor/template_form.html', {
            'form': form,
            'title': f'Editar: {template.name}',
            'template': template,
        })

    def post(self, request, pk):
        template = get_object_or_404(ProcessTemplate, pk=pk)
        form = ProcessTemplateForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            messages.success(request, _('Plantilla actualizada.'))
            return redirect('panel:gestor_template_detail', pk=pk)
        return render(request, 'panel/gestor/template_form.html', {
            'form': form,
            'title': f'Editar: {template.name}',
            'template': template,
        })


@method_decorator(login_required(login_url='/'), name='dispatch')
class GestorTemplateAddStepView(GestorRequiredMixin, View):
    """Add a step to a template."""

    def post(self, request, pk):
        template = get_object_or_404(ProcessTemplate, pk=pk)
        form = ProcessTemplateStepForm(request.POST)
        if form.is_valid():
            raw_order = request.POST.get('order', '').strip()
            try:
                new_order = int(raw_order) if raw_order else 0
            except (ValueError, TypeError):
                new_order = 0
            if new_order < 1:
                max_order = ProcessTemplateStep.objects.filter(
                    template=template
                ).aggregate(Max('order'))['order__max'] or 0
                new_order = max_order + 1
            else:
                ProcessTemplateStep.objects.filter(
                    template=template, order__gte=new_order
                ).update(order=F('order') + 1)
            step = form.save(commit=False)
            step.template = template
            step.order = new_order
            step.save()
            messages.success(request, _('Paso agregado a la plantilla.'))
        return redirect('panel:gestor_template_detail', pk=pk)


@method_decorator(login_required(login_url='/'), name='dispatch')
class GestorTemplateDeleteStepView(GestorRequiredMixin, View):
    """Delete a step from a template."""

    def post(self, request, template_pk, step_pk):
        template = get_object_or_404(ProcessTemplate, pk=template_pk)
        step = get_object_or_404(ProcessTemplateStep, pk=step_pk, template=template)
        deleted_order = step.order
        step.delete()
        ProcessTemplateStep.objects.filter(
            template=template, order__gt=deleted_order
        ).update(order=F('order') - 1)
        messages.success(request, _('Paso eliminado de la plantilla.'))
        return redirect('panel:gestor_template_detail', pk=template_pk)
