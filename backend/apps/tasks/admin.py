"""Admin configuration for tasks app."""

from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'assigned_to', 'created_at')
    list_filter = ('status', 'priority', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at', 'completed_at')

    fieldsets = (
        ('Información Básica', {
            'fields': ('title', 'description', 'status', 'priority')
        }),
        ('Asignación', {
            'fields': ('created_by', 'assigned_to')
        }),
        ('Fechas', {
            'fields': ('due_date', 'completed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
