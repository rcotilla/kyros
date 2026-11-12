"""
Documents app for kairos.

Manages file uploads, storage, and document tracking.

Fase 1: Basic document storage
Fase 2: Document management UI via Flet
Fase 3: AWS S3 / MinIO integration with django-storages
"""

from django.apps import AppConfig


class DocumentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.documents'
    verbose_name = 'Documentos'
