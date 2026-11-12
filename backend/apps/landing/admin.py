"""Admin configuration for landing app."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('name', 'email', 'message', 'ip_address', 'created_at')
    list_editable = ('status',)

    fieldsets = (
        (_('Información del Mensaje'), {
            'fields': ('name', 'email', 'message')
        }),
        (_('Metadatos'), {
            'fields': ('status', 'ip_address', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
