"""
Django Admin configuration for core app.

Enables admin interface for managing users, roles, and audit logs.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Role, UserProfile, Audit


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (_('Información Básica'), {
            'fields': ('name', 'description')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'status', 'company', 'created_at')
    list_filter = ('role', 'status', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'company')
    readonly_fields = ('created_at', 'updated_at', 'user')

    fieldsets = (
        (_('Usuario'), {
            'fields': ('user',)
        }),
        (_('Información del Rol'), {
            'fields': ('role', 'status')
        }),
        (_('Información Personal'), {
            'fields': ('company', 'phone')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """Override to add user to userprofile during creation."""
        super().save_model(request, obj, form, change)


@admin.register(Audit)
class AuditAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'model_name', 'timestamp', 'ip_address')
    list_filter = ('action', 'model_name', 'timestamp')
    search_fields = ('user__first_name', 'user__last_name', 'ip_address')
    readonly_fields = (
        'user', 'action', 'model_name', 'object_id',
        'details', 'ip_address', 'timestamp'
    )

    def has_add_permission(self, request):
        """Audit logs are read-only."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Audit logs are read-only."""
        return False

    fieldsets = (
        (_('Información de Auditoría'), {
            'fields': ('user', 'action', 'model_name', 'object_id')
        }),
        (_('Detalles'), {
            'fields': ('details', 'ip_address', 'timestamp'),
            'classes': ('collapse',)
        }),
    )
