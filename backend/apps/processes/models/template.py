"""
ProcessTemplate — reusable step blueprints for processes.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .types import ProcessType
from .step import ProcessStep


class ProcessTemplate(models.Model):
    """
    Reusable template for processes.

    Stores a set of steps that can be applied to any new process,
    avoiding the tedium of manually adding the same steps every time.
    """

    name = models.CharField(
        max_length=200,
        verbose_name=_('Nombre de la Plantilla')
    )
    process_type = models.ForeignKey(
        ProcessType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='templates',
        verbose_name=_('Tipo de Proceso'),
        help_text=_('Tipo de proceso al que aplica esta plantilla')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Descripción')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Activa')
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='process_templates',
        verbose_name=_('Creado por')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Plantilla de Proceso')
        verbose_name_plural = _('Plantillas de Proceso')
        ordering = ['process_type', 'name']

    def __str__(self):
        return self.name

    def apply_to(self, process):
        """Create ProcessStep records from this template's steps."""
        for tpl_step in self.template_steps.all():
            ProcessStep.objects.create(
                process=process,
                name=tpl_step.name,
                description=tpl_step.description,
                order=tpl_step.order,
                status='pending',
                due_date=None,
            )
        return self.template_steps.count()


class ProcessTemplateStep(models.Model):
    """
    A single step within a process template.

    These are the blueprint steps that get copied into ProcessStep
    records when a template is applied to a process.
    """

    template = models.ForeignKey(
        ProcessTemplate,
        on_delete=models.CASCADE,
        related_name='template_steps',
        verbose_name=_('Plantilla')
    )
    name = models.CharField(
        max_length=200,
        verbose_name=_('Nombre del Paso')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Descripción')
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Orden')
    )
    estimated_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Días Estimados'),
        help_text=_('Días estimados para completar este paso')
    )

    class Meta:
        verbose_name = _('Paso de Plantilla')
        verbose_name_plural = _('Pasos de Plantilla')
        ordering = ['order']

    def __str__(self):
        return f"{self.template.name} → {self.name}"
