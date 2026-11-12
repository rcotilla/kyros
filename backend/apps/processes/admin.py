"""Admin configuration for processes app."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import ProcessType, Process, ProcessStep


@admin.register(ProcessType)
class ProcessTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'estimated_days', 'is_active', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


class ProcessStepInline(admin.TabularInline):
    model = ProcessStep
    extra = 0
    ordering = ['order']


@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = (
        'file_number', 'title', 'client', 'process_type',
        'status', 'priority', 'gestor', 'due_date', 'created_at'
    )
    list_filter = ('status', 'priority', 'process_type__category', 'created_at')
    search_fields = (
        'file_number', 'title', 'description',
        'client__first_name', 'client__last_name',
        'external_reference', 'notes'
    )
    readonly_fields = ('file_number', 'created_at', 'updated_at', 'created_by')
    list_editable = ('status', 'priority')
    inlines = [ProcessStepInline]

    fieldsets = (
        (_('Identificación'), {
            'fields': ('file_number', 'title', 'description')
        }),
        (_('Relaciones'), {
            'fields': ('process_type', 'client')
        }),
        (_('Estado y Prioridad'), {
            'fields': ('status', 'priority')
        }),
        (_('Asignación'), {
            'fields': ('gestor', 'operator')
        }),
        (_('Fechas'), {
            'fields': ('start_date', 'due_date', 'submission_date', 'completion_date'),
            'classes': ('collapse',)
        }),
        (_('Información Adicional'), {
            'fields': ('external_reference', 'notes'),
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


@admin.register(ProcessStep)
class ProcessStepAdmin(admin.ModelAdmin):
    list_display = ('name', 'process', 'order', 'status', 'assigned_to', 'due_date')
    list_filter = ('status', 'process__status')
    search_fields = ('name', 'description', 'process__file_number')
    readonly_fields = ('created_at', 'updated_at', 'completed_at')
