from rest_framework.permissions import BasePermission


class IsChatMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj in request.user.chats.all()


class IsGroupMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj in request.user.groups.all()
