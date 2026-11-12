"""
ASGI config for kairos project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/

Fase 2: Django Channels para WebSockets (notificaciones en tiempo real)
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kairos.settings')

django_asgi_app = get_asgi_application()

# TODO: Fase 2 - Importar consumers de WebSocket
# from apps.notifications.consumers import NotificationConsumer

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    # TODO: Fase 2 - WebSocket routing
    # "websocket": AuthMiddlewareStack(
    #     URLRouter([
    #         path("ws/notifications/", NotificationConsumer.as_asgi()),
    #     ])
    # ),
})
