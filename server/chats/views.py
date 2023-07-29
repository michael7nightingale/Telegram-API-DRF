from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from http import HTTPStatus

from rest_framework.serializers import Serializer

from users.models import Account
from .models import Chat
from .permissions import IsChatMember
from .serializers import ChatCreateSerializer, ChatListSerializer, ChatDetailSerializer


class ChatViewSet(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    queryset = Chat.objects.all()
    lookup_field = "id"
    lookup_url_kwarg = "chat_id"

    def get_permissions(self):
        pc = [IsAuthenticated]
        if self.action in ("retrieve", "destroy", "update"):
            pc.append(IsChatMember)
        return [p() for p in pc]

    def get_serializer(self, *args, **kwargs) -> Serializer:
        match self.action:
            case "create":
                s = ChatCreateSerializer
            case "list":
                s = ChatListSerializer
            case "retrieve":
                s = ChatDetailSerializer
            case _:
                raise AssertionError("No way to access this default.")
        return s(*args, **kwargs)

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        account_id = serializer.validated_data.get('account_id')
        if account_id == request.user:
            return Response(
                {
                    "detail": "Other user required",
                },
                status=HTTPStatus.BAD_REQUEST
            )
        if account_id is None:
            return Response(
                status=HTTPStatus.BAD_REQUEST,
                data={
                    "detail": "account id is required"
                }
            )

        try:
            account = Account.objects.get(pk=account_id)
        except Account.DoesNotExist:
            return Response(
                {
                    "detail": "Account is not found"
                },
                status=HTTPStatus.NOT_FOUND
            )
        serializer.save(members=[request.user, account])
        return Response("Chat created")

    def list(self, request, *args, **kwargs):
        chats = Chat.objects.all_account_chats(request.user)
        serializer = self.get_serializer(chats, many=True)
        return Response(serializer.data)
