"""Models for tasks app."""

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Task(models.Model):
    """
    Work task/ticket in the system.

    Represents a request from a client that flows through
    manager approval -> operator processing -> completion.
    """

    STATUS_CHOICES = (
        ('pending', _('Pendiente')),
        ('assigned', _('Asignada')),
        ('in_progress', _('En Proceso')),
        ('review', _('Revisión')),
        ('completed', _('Completada')),
        ('rejected', _('Rechazada')),
    )

    PRIORITY_CHOICES = (
        ('low', _('Baja')),
        ('medium', _('Media')),
        ('high', _('Alta')),
        ('urgent', _('Urgente')),
    )

    title = models.CharField(
        max_length=255,
        verbose_name=_('Título')
    )

    description = models.TextField(
        verbose_name=_('Descripción')
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Estado')
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name=_('Prioridad')
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='tasks_created',
        verbose_name=_('Creado por')
    )

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks_assigned',
        verbose_name=_('Asignado a')
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Fecha de Creación')
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Última Actualización')
    )

    due_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Fecha de Vencimiento')
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Fecha de Completación')
    )

    class Meta:
        verbose_name = _('Tarea')
        verbose_name_plural = _('Tareas')
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['assigned_to', 'status']),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
