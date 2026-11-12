"""
URL configuration for kairos project.

API v1 endpoints for mobile/extensibility.
Panel for working views.
Landing page for public access.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # API v1 — namespaced for mobile/extensibility
    path('api/v1/auth/', include('apps.core.urls')),
    path('api/v1/clients/', include('apps.clients.urls')),
    path('api/v1/processes/', include('apps.processes.urls')),
    path('api/v1/documents/', include('apps.documents.urls')),
    path('api/v1/docgen/', include('docgen.urls')),
    path('api/v1/tasks/', include('apps.tasks.urls')),

    # Panel de trabajo (authenticated users)
    path('panel/', include('apps.panel.urls')),

    # Landing page (public)
    path('', include('apps.landing.urls')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
