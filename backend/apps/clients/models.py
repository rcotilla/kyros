"""
Models for clients app.

Client management for the gestoría platform.
Each client represents a person or entity that uses the gestoría's services.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from apps.core.constants import COUNTRY_CHOICES


class Client(models.Model):
    """
    Client of the gestoría.

    Stores personal information, contact details, and identification
    needed for administrative processes (extranjería, marcas, etc.).
    """

    DOCUMENT_TYPE_CHOICES = (
        ('dni', 'DNI'),
        ('nie', 'NIE'),
        ('pasaporte', 'Pasaporte'),
        ('cuit', 'CUIT'),
        ('cuil', 'CUIL'),
        ('otro', 'Otro'),
    )

    STATUS_CHOICES = (
        ('active', _('Activo')),
        ('inactive', _('Inactivo')),
    )

    # Identification
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPE_CHOICES,
        verbose_name=_('Tipo de Documento')
    )
    document_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('Número de Documento')
    )
    document_issuing_country = models.CharField(
        max_length=2,
        blank=True,
        choices=COUNTRY_CHOICES,
        verbose_name=_('País de Expedición'),
        help_text=_('País donde se expidió el documento')
    )

    # Personal info
    first_name = models.CharField(
        max_length=150,
        verbose_name=_('Nombre')
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name=_('Apellido')
    )
    nationality = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Nacionalidad')
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Fecha de Nacimiento')
    )

    # Contact
    email = models.EmailField(
        blank=True,
        verbose_name=_('Email')
    )
    phone_regex = RegexValidator(
        regex=r'^\+?[\d\s\-]{7,20}$',
        message=_('Formato de teléfono inválido')
    )
    phone = models.CharField(
        validators=[phone_regex],
        max_length=20,
        blank=True,
        verbose_name=_('Teléfono')
    )
    phone_secondary = models.CharField(
        validators=[phone_regex],
        max_length=20,
        blank=True,
        verbose_name=_('Teléfono Secundario')
    )

    # Address
    address = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_('Dirección')
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Ciudad')
    )
    province = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Provincia')
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Código Postal')
    )
    country = models.CharField(
        max_length=2,
        default='AR',
        choices=COUNTRY_CHOICES,
        verbose_name=_('País')
    )

    # Metadata
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notas'),
        help_text=_('Notas internas sobre el cliente')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name=_('Estado')
    )

    # Relations
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clients_assigned',
        verbose_name=_('Asignado a'),
        help_text=_('Gestor responsable del cliente')
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='clients_created',
        verbose_name=_('Creado por')
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Cliente')
        verbose_name_plural = _('Clientes')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['document_type', 'document_number']),
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['status', '-created_at']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.document_number})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
