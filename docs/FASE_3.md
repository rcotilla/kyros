# Fase 3: Automatización Avanzada

Documentación de features a implementar en Fase 3 del proyecto KAIROS.

## 1. Generación de PDFs (WeasyPrint)

### Objetivo
Convertir documentos HTML a PDF con calidad de imprenta para reportes y documentos procesados.

### Implementación

```python
# apps/documents/services/pdf_generator.py
from weasyprint import HTML, CSS

def generate_pdf(html_content, output_path):
    """Genera PDF desde HTML."""
    HTML(string=html_content).write_pdf(output_path)
    return output_path

def generate_report_pdf(task_id):
    """Genera reporte PDF de una tarea completada."""
    task = Task.objects.get(id=task_id)
    html = render_to_string('reports/task_report.html', {'task': task})
    return generate_pdf(html, f'media/reports/{task_id}.pdf')
```

### Templates
- `templates/reports/task_report.html` - Plantilla de reporte
- `templates/reports/invoice.html` - Plantilla de factura

## 2. Procesamiento Asincrónico (Celery + Redis)

### Objetivo
Ejecutar tareas pesadas sin bloquear la aplicación.

### Tareas Principales
1. **Generación de PDFs** - async_generate_pdf()
2. **Envío de emails** - async_send_notification_email()
3. **Procesamiento de archivos** - async_process_document()
4. **Generación de reportes** - async_generate_report()

### Configuración

```python
# kairos/celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kairos.settings')

app = Celery('kairos')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# settings.py
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
```

### Ejecución
```bash
# Terminal 1: Broker Redis
redis-server

# Terminal 2: Worker de Celery
celery -A kairos worker -l info

# Terminal 3: Beat (tareas programadas)
celery -A kairos beat -l info
```

## 3. Almacenamiento AWS S3 / MinIO

### Objetivo
Almacenar archivos en la nube con escalabilidad y seguridad.

### Instalación
```bash
pip install django-storages boto3
```

### Configuración (settings.py)

```python
# AWS S3
if not DEBUG:  # Solo en producción
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        },
        "staticfiles": {
            "BACKEND": "storages.backends.s3boto3.S3StaticStorage",
        },
    }

    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = 'us-east-1'
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'

# MinIO (alternativa local)
elif os.getenv('USE_MINIO'):
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
            "OPTIONS": {
                "ACCESS_KEY": os.getenv('MINIO_ACCESS_KEY'),
                "SECRET_KEY": os.getenv('MINIO_SECRET_KEY'),
                "STORAGE_BUCKET_NAME": 'kairos',
                "ENDPOINT_URL": 'http://localhost:9000',
            }
        }
    }
```

## 4. Sistema de Alertas por Email

### Objetivo
Notificar a usuarios sobre cambios de estado, asignaciones, etc.

### Implementación

```python
# apps/notifications/services/email_service.py
from django.core.mail import send_mail
from django.template.loader import render_to_string

def notify_task_assigned(task, operator):
    """Envía email de asignación de tarea."""
    context = {'task': task, 'operator': operator}
    html = render_to_string('emails/task_assigned.html', context)
    send_mail(
        f'Nueva Tarea Asignada: {task.title}',
        strip_tags(html),
        'noreply@kairos.local',
        [operator.email],
        html_message=html,
    )

def notify_task_completed(task, client):
    """Envía email cuando tarea se completa."""
    context = {'task': task, 'download_url': task.get_download_url()}
    # ... similar
```

### Triggers
- Tarea asignada
- Tarea completada
- Documento cargado
- Cambio de estado

## 5. Permisos a Nivel de Objeto (django-guardian)

### Objetivo
Control fino de permisos: "Usuario A solo puede ver Documento X".

### Instalación
```bash
pip install django-guardian
```

### Configuración

```python
# settings.py
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
]

# apps/documents/models.py
from guardian.shortcuts import assign_perm, remove_perm

def grant_document_access(document, user):
    """Otorga acceso a un documento específico."""
    assign_perm('view_document', user, document)
    assign_perm('download_document', user, document)

def revoke_document_access(document, user):
    """Revoca acceso a un documento."""
    remove_perm('view_document', user, document)
```

## 6. WebSockets (Django Channels)

### Objetivo
Notificaciones en tiempo real sin refrescar la página.

### Configuración
```python
# kairos/asgi.py - Ya configurado
# apps/notifications/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("notifications", self.channel_name)
        await self.accept()

    async def notification_message(self, event):
        await self.send(text_data=json.dumps(event))
```

### Cliente (Flet - Fase 2)
```python
import websockets
import json

async def listen_notifications():
    async with websockets.connect('ws://localhost:8000/ws/notifications/') as ws:
        async for message in ws:
            data = json.loads(message)
            print(f"Notificación: {data}")
```

## 7. Monitoreo y Logging

### Objetivo
Rastrear errores y performance.

### Herramientas
- Sentry para error tracking
- ELK Stack (Elasticsearch, Logstash, Kibana)
- New Relic para APM

### Setup Sentry
```bash
pip install sentry-sdk
```

```python
# settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="https://examplePublicKey@o0.ingest.sentry.io/0",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
)
```

## 8. Testing Completo

### Coverage
```bash
pytest --cov=apps backend/
```

### E2E (End-to-End)
- Selenium para testing de UI
- Pytest-asyncio para WebSockets

## Timeline Estimado

| Componente | Estimación | Dependencias |
|------------|-----------|--------------|
| PDF Generation | 1-2 semanas | - |
| Celery + Redis | 2-3 semanas | Redis setup |
| S3 Integration | 1-2 semanas | AWS account |
| Email Alerts | 1-2 semanas | Email backend |
| Object Permissions | 1-2 semanas | django-guardian |
| WebSockets | 2-3 semanas | Channels configurado |
| Monitoring | 1-2 semanas | Sentry/ELK setup |

## Variables de Entorno (Fase 3)

```env
# Redis
REDIS_URL=redis://localhost:6379/0

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password

# AWS S3
USE_S3=True
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_STORAGE_BUCKET_NAME=kairos-files
AWS_S3_REGION_NAME=us-east-1

# MinIO (alternativa)
USE_MINIO=False
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_ENDPOINT=localhost:9000

# Sentry
SENTRY_DSN=https://key@sentry.io/project
```

---

**Nota**: Esta documentación se actualiza conforme avanza el desarrollo. Ver `README.md` para estado general del proyecto.
