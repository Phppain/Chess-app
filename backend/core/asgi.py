import os
import django

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()  # 👈 ОБЯЗАТЕЛЬНО перед импортом GameConsumer

from .consumers import GameConsumer  # теперь безопасно

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/chess/<game_id>/", GameConsumer.as_asgi()),
        ])
    ),
})