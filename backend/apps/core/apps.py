"""
Core app configuration for kairos.

Manages:
- User authentication and roles
- Base models
- Permissions and groups
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = 'Core'
