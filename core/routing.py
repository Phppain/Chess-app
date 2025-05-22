# ws_routing.py
from django.urls import path
from .consumers import ChessConsumer

websocket_urlpatterns = [
    path('ws/chess/<int:game_id>/', ChessConsumer.as_asgi()),
]