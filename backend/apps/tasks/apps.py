"""Tasks app for kairos.

Manages work tasks, assignments, and status tracking.

Fase 1: Basic task model and status tracking
Fase 2: Task assignments and notifications via Flet
Fase 3: Complex workflows and automations
"""

from django.apps import AppConfig


class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.tasks'
    verbose_name = 'Tareas'
