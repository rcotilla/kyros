"""Models for landing app."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class ContactMessage(models.Model):
    """Contact form submission from the landing page."""

    STATUS_CHOICES = (
        ('pending', _('Pendiente')),
        ('read', _('Leído')),
        ('replied', _('Respondido')),
        ('archived', _('Archivado')),
    )

    name = models.CharField(
        max_length=255,
        verbose_name=_('Nombre')
    )
    email = models.EmailField(
        verbose_name=_('Email')
    )
    message = models.TextField(
        verbose_name=_('Mensaje')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Estado')
    )
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name=_('Dirección IP')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Fecha de Envío')
    )

    class Meta:
        verbose_name = _('Mensaje de Contacto')
        verbose_name_plural = _('Mensajes de Contacto')
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.name} <{self.email}> - {self.created_at:%d/%m/%Y}"
