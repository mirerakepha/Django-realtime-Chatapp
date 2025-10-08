
from django.urls import re_path, path
from .consumers import ChatroomConsumer, OnlineStatusConsumer

websocket_urlpatterns = [
    re_path(r"^ws/chatroom/(?P<chatroom_name>[^/]+)/$", ChatroomConsumer.as_asgi()),
    path("ws/online-status/", OnlineStatusConsumer.as_asgi()),
]