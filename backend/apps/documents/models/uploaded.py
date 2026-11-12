"""
Document — an uploaded file attached to a client or process.

This is the model for SUBMITTED documents: scanned files, forms,
certificates, etc. that are attached to a specific gestion.
"""

import re
import unicodedata

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator


def _safe_slug(value):
    """Normalize a name/path segment to a filesystem-safe slug.

    Strips accents, keeps letters/digits/spaces, collapses the rest.
    """
    if not value:
        return 'sin_asignar'
    value = unicodedata.normalize('NFKD', str(value)).encode('ascii', 'ignore').decode('ascii')
    value = value.strip().replace(' ', '_')
    value = re.sub(r'[^a-zA-Z0-9._-]', '', value)
    return value or 'sin_asignar'


def document_upload_path(instance, filename):
    """Build upload path: documents/<client>/<process_type>/<file_number>/<file>.

    Files are grouped per client, then per process type and file number,
    so they can be synced to an external server and accessed directly
    in an emergency (e.g. system down).
    """
    parts = ['documents']

    if instance.client:
        client_name = _safe_slug(instance.client.full_name)
    else:
        client_name = 'sin_cliente'
    parts.append(client_name)

    if instance.process and instance.process.process_type:
        process_type = _safe_slug(instance.process.process_type.name)
    else:
        process_type = 'sin_tipo'
    parts.append(process_type)

    if instance.process:
        file_number = _safe_slug(instance.process.file_number)
    else:
        file_number = 'sin_expediente'
    parts.append(file_number)

    return '{}/{}'.format('/'.join(parts), filename)


class Document(models.Model):
    """
    Uploaded document attached to a client or process.

    Tracks file uploads with classification.
    """

    TYPE_CHOICES = (
        ('original', _('Documento Original')),
        ('processed', _('Documento Procesado')),
        ('evidence', _('Evidencia')),
        ('report', _('Reporte')),
        ('form', _('Formulario')),
        ('certificate', _('Certificado')),
        ('contract', _('Contrato')),
    )

    # Relations
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name=_('Propietario')
    )
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='documents',
        verbose_name=_('Cliente')
    )
    process = models.ForeignKey(
        'processes.Process',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='documents',
        verbose_name=_('Proceso')
    )

    # Document info
    title = models.CharField(
        max_length=255,
        verbose_name=_('Título')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Descripción')
    )
    file = models.FileField(
        upload_to=document_upload_path,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png']
            )
        ],
        verbose_name=_('Archivo')
    )
    doc_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='original',
        verbose_name=_('Tipo de Documento')
    )
    file_size = models.BigIntegerField(
        editable=False,
        verbose_name=_('Tamaño del Archivo (bytes)')
    )

    # Metadata
    is_public = models.BooleanField(
        default=False,
        verbose_name=_('Es Público'),
        help_text=_('Si está marcado, todos pueden ver este documento')
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Documento')
        verbose_name_plural = _('Documentos')
        ordering = ('-uploaded_at',)
        indexes = [
            models.Index(fields=['owner', '-uploaded_at']),
            models.Index(fields=['client', '-uploaded_at']),
            models.Index(fields=['process', '-uploaded_at']),
            models.Index(fields=['doc_type']),
        ]

    def __str__(self):
        parts = [self.title]
        if self.client:
            parts.append(f"Cliente: {self.client}")
        if self.process:
            parts.append(f"Proceso: {self.process.file_number}")
        return " - ".join(parts)

    def save(self, *args, **kwargs):
        """Update file size before saving."""
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)
