from django.urls import path, include, re_path

from .views import AccountViewSet


urlpatterns = [
    path("users/", AccountViewSet.as_view({"post": "create"}), name="users"),
    path('', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),

]
