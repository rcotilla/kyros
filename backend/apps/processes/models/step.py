"""
ProcessStep — individual step within a process.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .process import Process


class ProcessStep(models.Model):
    """
    Step within a process.

    Represents a specific action or milestone in the process workflow.
    Used for tracking progress and generating PDF reports.
    """

    STATUS_CHOICES = (
        ('pending', _('Pendiente')),
        ('in_progress', _('En Proceso')),
        ('completed', _('Completado')),
        ('skipped', _('Omitido')),
    )

    process = models.ForeignKey(
        Process,
        on_delete=models.CASCADE,
        related_name='steps',
        verbose_name=_('Proceso')
    )
    name = models.CharField(
        max_length=200,
        verbose_name=_('Nombre')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Descripción')
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Orden')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Estado')
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='process_steps',
        verbose_name=_('Asignado a')
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Fecha de Vencimiento')
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Fecha de Completación')
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notas')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Paso del Proceso')
        verbose_name_plural = _('Pasos del Proceso')
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.process.file_number} - {self.name}"
