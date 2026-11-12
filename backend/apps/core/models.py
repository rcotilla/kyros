"""
Core models for kairos.

Defines user roles and base models for the entire system.

Roles:
- CLIENT: Submits requests and uploads original documentation
- MANAGER: Reviews and assigns tasks to operators
- OPERATOR: Processes tasks and uploads resolved files
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Role(models.Model):
    """
    User roles in the system.

    Fase 1: Basic roles (Client, Manager, Operator)
    Fase 2: Extended with Flet-specific permissions
    Fase 3: Object-level permissions via django-guardian
    """

    ROLE_CHOICES = (
        ('client', _('Cliente')),
        ('manager', _('Gestor')),
        ('operator', _('Operador')),
        ('admin', _('Administrador')),
    )

    name = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        unique=True,
        verbose_name=_('Nombre del Rol')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Descripción')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Rol')
        verbose_name_plural = _('Roles')
        ordering = ('name',)

    def __str__(self):
        return self.get_name_display()


class UserProfile(models.Model):
    """
    Extended user profile with role and additional metadata.

    Links to Django's built-in User model and adds:
    - Role assignment
    - Company/Organization
    - Contact information
    - Status tracking
    """

    STATUS_CHOICES = (
        ('active', _('Activo')),
        ('inactive', _('Inactivo')),
        ('suspended', _('Suspendido')),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('Usuario')
    )

    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        verbose_name=_('Rol'),
        help_text=_('Rol principal del usuario en el sistema')
    )

    company = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Empresa/Organización')
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Teléfono')
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name=_('Estado')
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Perfil de Usuario')
        verbose_name_plural = _('Perfiles de Usuarios')
        ordering = ('-created_at',)

    def __str__(self):
        display_name = self.user.get_full_name() or self.user.username
        return f"{display_name} ({self.get_role_display()})"

    def get_role_display(self):
        return self.role.get_name_display()


class Audit(models.Model):
    """
    Audit log for tracking user actions.

    Records who did what, when, and where for security and compliance.
    """

    ACTION_CHOICES = (
        ('create', _('Crear')),
        ('update', _('Actualizar')),
        ('delete', _('Eliminar')),
        ('view', _('Ver')),
        ('download', _('Descargar')),
        ('upload', _('Subir')),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs',
        verbose_name=_('Usuario')
    )

    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name=_('Acción')
    )

    model_name = models.CharField(
        max_length=100,
        verbose_name=_('Modelo')
    )

    object_id = models.PositiveIntegerField(
        verbose_name=_('ID del Objeto')
    )

    details = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Detalles')
    )

    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name=_('Dirección IP')
    )

    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Timestamp')
    )

    class Meta:
        verbose_name = _('Auditoría')
        verbose_name_plural = _('Auditorías')
        ordering = ('-timestamp',)
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['model_name', 'object_id']),
        ]

    def __str__(self):
        return f"{self.user} - {self.get_action_display()} ({self.timestamp})"
