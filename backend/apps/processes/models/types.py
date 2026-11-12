"""
ProcessType — categories of administrative procedures.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class ProcessType(models.Model):
    """
    Type of administrative process.

    Defines the categories of procedures the gestoría handles:
    extranjería, marcas, constituciones, etc.
    """

    CATEGORY_CHOICES = (
        ('extranjeria', _('Extranjería')),
        ('marcas', _('Marcas')),
        ('constituciones', _('Constituciones')),
        ('contabilidad', _('Contabilidad')),
        ('legal', _('Legal')),
        ('otro', _('Otro')),
    )

    name = models.CharField(
        max_length=200,
        verbose_name=_('Nombre')
    )
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        verbose_name=_('Categoría')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Descripción')
    )
    estimated_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Días Estimados'),
        help_text=_('Tiempo estimado de duración del proceso')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Activo')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Tipo de Proceso')
        verbose_name_plural = _('Tipos de Proceso')
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.get_category_display()} - {self.name}"
