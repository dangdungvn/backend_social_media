"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

# Ứng dụng Django
django_asgi_app = get_asgi_application()

# Import các consumers cho WebSocket sau khi settings đã được cấu hình
from chat.consumers import ChatConsumer
from .whitenoise_middleware import ASGIStaticFilesHandler

# Định tuyến WebSocket
websocket_urlpatterns = [
    path("ws/chat/<str:room_name>/", ChatConsumer.as_asgi()),
]

# Cấu hình ứng dụng ASGI với ProtocolTypeRouter
application = ProtocolTypeRouter(
    {
        "http": ASGIStaticFilesHandler(django_asgi_app),
        "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
    }
)
