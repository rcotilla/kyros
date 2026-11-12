"""Admin configuration for clients app."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = (
        'full_name', 'document_type', 'document_number',
        'email', 'phone', 'status', 'assigned_to', 'created_at'
    )
    list_filter = ('status', 'document_type', 'country', 'created_at')
    search_fields = (
        'first_name', 'last_name', 'document_number',
        'email', 'phone', 'notes'
    )
    readonly_fields = ('created_at', 'updated_at', 'created_by')
    list_editable = ('status',)

    fieldsets = (
        (_('Datos Personales'), {
            'fields': ('first_name', 'last_name', 'birth_date')
        }),
        (_('Identificación'), {
            'fields': ('document_type', 'document_number', 'document_issuing_country')
        }),
        (_('Contacto'), {
            'fields': ('email', 'phone', 'phone_secondary')
        }),
        (_('Gestión'), {
            'fields': ('nationality', 'status', 'assigned_to')
        }),
        (_('Domicilio'), {
            'fields': ('address', 'city', 'province', 'postal_code', 'country'),
            'classes': ('collapse',)
        }),
        (_('Notas'), {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        (_('Metadata'), {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
