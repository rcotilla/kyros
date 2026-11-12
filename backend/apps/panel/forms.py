"""Forms for panel views."""

from django import forms
from django.utils.translation import gettext_lazy as _
from apps.clients.models import Client
from apps.processes.models import (
    Process, ProcessType, ProcessStep,
    ProcessTemplate, ProcessTemplateStep,
)
from apps.documents.models import Document
from .forms_base import BootstrapForm


class ClientForm(BootstrapForm):
    """Form for creating/editing clients."""

    class Meta:
        model = Client
        fields = [
            'first_name', 'last_name', 'birth_date',
            'document_type', 'document_number', 'document_issuing_country',
            'nationality', 'email', 'phone', 'phone_secondary',
            'address', 'city', 'province', 'postal_code', 'country',
            'notes',
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class ProcessForm(BootstrapForm):
    """Form for creating/editing processes."""

    template = forms.ModelChoiceField(
        queryset=ProcessTemplate.objects.filter(is_active=True),
        required=False,
        label=_('Plantilla'),
        help_text=_('Seleccionar una plantilla para crear los pasos automáticamente'),
        empty_label=_('— Sin plantilla —'),
    )

    class Meta:
        model = Process
        fields = [
            'title', 'description',
            'process_type', 'client',
            'status', 'priority',
            'gestor', 'operator',
            'start_date', 'due_date', 'submission_date', 'completion_date',
            'notes', 'external_reference',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'submission_date': forms.DateInput(attrs={'type': 'date'}),
            'completion_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['template'].queryset = ProcessTemplate.objects.filter(is_active=True)


class ProcessStepForm(BootstrapForm):
    """Form for adding steps to a process."""

    class Meta:
        model = ProcessStep
        fields = ['name', 'description', 'status', 'assigned_to', 'due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 2}),
        }


class DocumentUploadForm(BootstrapForm):
    """Form for uploading documents."""

    class Meta:
        model = Document
        fields = ['title', 'doc_type', 'client', 'process', 'file', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }


class ProcessFilterForm(forms.Form):
    """Filter form for process lists."""

    STATUS_CHOICES = [('', 'Todos')] + list(Process.STATUS_CHOICES)
    PRIORITY_CHOICES = [('', 'Todas')] + list(Process.PRIORITY_CHOICES)

    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False, label='Estado')
    priority = forms.ChoiceField(choices=PRIORITY_CHOICES, required=False, label='Prioridad')
    search = forms.CharField(required=False, label='Buscar', widget=forms.TextInput(attrs={'placeholder': 'Expediente, título...'}))


class ProcessTemplateForm(BootstrapForm):
    """Form for creating/editing process templates."""

    class Meta:
        model = ProcessTemplate
        fields = ['name', 'process_type', 'description', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class ProcessTemplateStepForm(BootstrapForm):
    """Form for adding steps to a template."""

    class Meta:
        model = ProcessTemplateStep
        fields = ['name', 'description', 'estimated_days']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }
