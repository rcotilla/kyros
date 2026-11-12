"""
Process — individual administrative procedure (expediente).
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from apps.clients.models import Client
from .types import ProcessType


class Process(models.Model):
    """
    Administrative process (expediente).

    Represents a specific procedure being handled for a client.
    Tracks status, assigned staff, key dates, and linked documents.
    """

    STATUS_CHOICES = (
        ('draft', _('Borrador')),
        ('pending', _('Pendiente')),
        ('in_progress', _('En Trámite')),
        ('review', _('Revisión')),
        ('waiting_client', _('Esperando Cliente')),
        ('submitted', _('Presentado')),
        ('approved', _('Aprobado')),
        ('rejected', _('Rechazado')),
        ('completed', _('Completado')),
        ('closed', _('Cerrado')),
    )

    PRIORITY_CHOICES = (
        ('low', _('Baja')),
        ('medium', _('Media')),
        ('high', _('Alta')),
        ('urgent', _('Urgente')),
    )

    # Identification
    file_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        verbose_name=_('Número de Expediente'),
        help_text=_('Se genera automáticamente si se deja vacío')
    )
    title = models.CharField(
        max_length=300,
        verbose_name=_('Título')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Descripción')
    )

    # Relations
    process_type = models.ForeignKey(
        ProcessType,
        on_delete=models.PROTECT,
        related_name='processes',
        verbose_name=_('Tipo de Proceso')
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='processes',
        verbose_name=_('Cliente')
    )

    # Status & Priority
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name=_('Estado')
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name=_('Prioridad')
    )

    # Assignment
    gestor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processes_gestor',
        verbose_name=_('Gestor Asignado')
    )
    operator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processes_operator',
        verbose_name=_('Operador Asignado')
    )

    # Dates
    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Fecha de Inicio')
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Fecha de Vencimiento')
    )
    submission_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Fecha de Presentación')
    )
    completion_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Fecha de Finalización')
    )

    # Additional info
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notas Internas')
    )
    external_reference = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Referencia Externa'),
        help_text=_('Número de expediente o referencia de organismos externos')
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='processes_created',
        verbose_name=_('Creado por')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Proceso')
        verbose_name_plural = _('Procesos')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['client', 'status']),
            models.Index(fields=['gestor', 'status']),
            models.Index(fields=['process_type', 'status']),
        ]

    def __str__(self):
        return f"[{self.file_number}] {self.title}"

    def save(self, *args, **kwargs):
        if not self.file_number:
            last_process = Process.objects.order_by('-id').first()
            next_num = (last_process.id + 1) if last_process else 1
            self.file_number = f"EXP-{next_num:05d}"
        super().save(*args, **kwargs)
