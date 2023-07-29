from django.urls import path, include

from chats.routing import websocket_urlpatterns as wu


websocket_urlpatterns = [

]

websocket_urlpatterns += wu

