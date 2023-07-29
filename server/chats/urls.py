from django.urls import path, include

from .views import ChatViewSet
from .routers import ChatRouter


router = ChatRouter()
router.register("chats", ChatViewSet, "chats")


urlpatterns = [
    path("", include(router.urls)),

]
