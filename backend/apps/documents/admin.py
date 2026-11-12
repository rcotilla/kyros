"""Admin configuration for documents app."""

from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'owner', 'doc_type', 'client', 'process',
        'file_size', 'uploaded_at'
    )
    list_filter = ('doc_type', 'uploaded_at', 'is_public')
    search_fields = (
        'title', 'description', 'owner__first_name', 'owner__last_name',
        'client__first_name', 'client__last_name',
        'process__file_number'
    )
    readonly_fields = ('file_size', 'uploaded_at', 'updated_at', 'owner')

    fieldsets = (
        ('Información del Documento', {
            'fields': ('title', 'description', 'doc_type')
        }),
        ('Archivo', {
            'fields': ('file', 'file_size', 'owner')
        }),
        ('Relaciones', {
            'fields': ('client', 'process')
        }),
        ('Configuración', {
            'fields': ('is_public',)
        }),
        ('Timestamps', {
            'fields': ('uploaded_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
