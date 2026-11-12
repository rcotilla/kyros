"""Landing app for kairos.

Public landing page and static information.

Fase 1: Basic landing page with project info
Fase 2: Extended with Flet dashboard
Fase 3: SEO optimization and analytics
"""

from django.apps import AppConfig


class LandingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.landing'
    verbose_name = 'Landing'
