# chat/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/chat/async$", consumers.ChatAsyncConsumer.as_asgi()),
    re_path(r"ws/chat/sync$", consumers.ChatSyncConsumer.as_asgi()),
]