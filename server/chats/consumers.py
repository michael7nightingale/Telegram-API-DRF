from rest_framework.exceptions import PermissionDenied
from channels.db import database_sync_to_async
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.decorators import action
from rest_framework.serializers import Serializer
from djangochannelsrestframework.scope_utils import ensure_async
from djangochannelsrestframework.observer.generics import ObserverModelInstanceMixin
from asgiref.sync import sync_to_async

from users.models import Account
from .serializers import (
    ChatListSerializer, ChatCreateSerializer, ChatDetailSerializer,
    MessageDetailSerializer, MessageCreateSerializer,
)
from .models import Chat, Group, message_types_models


class RequestImitator:
    def __init__(self, user):
        self.user = user


class ChatConsumer(ObserverModelInstanceMixin,
                   GenericAsyncAPIConsumer):
    queryset = Chat.objects.all()
    serializer_class = ChatListSerializer

    @database_sync_to_async
    def get_serializer(self, action_kwargs: dict | None = None, *args, **kwargs) -> Serializer:
        action_ = action_kwargs.get("action")
        match action_:
            case "chat_list":
                s = ChatListSerializer
            case "chat_create":
                s = ChatCreateSerializer
            case "chat_detail":
                s = ChatDetailSerializer
            case "message_detail":
                s = MessageDetailSerializer
            case "send_message":
                s = MessageCreateSerializer
            case _:
                raise AssertionError(f"Please define action {action_}")
        return s(*args, **kwargs)

    @database_sync_to_async
    def get_serializer_data(self, serializer: Serializer):
        return serializer.data

    async def websocket_connect(self, message):
        try:
            for permission in await self.get_permissions(action="connect"):
                if not await ensure_async(permission.can_connect)(
                        scope=self.scope, consumer=self, message=message
                ):
                    raise PermissionDenied()
            await self.accept()
            self.account = self.scope['user']
            self.account_id = str(self.account.id)
            await self.add_group(self.account_id)
        except PermissionDenied:
            await self.close()

    @database_sync_to_async
    def save_serializer(self, serializer: Serializer, **kwargs):
        return serializer.save(**kwargs)

    @action()
    async def chat_list(self, **kwargs):
        queryset = await sync_to_async(Chat.objects.all_account_chats)(self.account)
        serializer = await self.get_serializer(action_kwargs=kwargs, instance=queryset, many=True)
        await self.send_json(
            content=await self.get_serializer_data(serializer)
        )

    @action()
    async def chat_create(self, **kwargs):
        action_kwargs = {
            "action": kwargs['action'],
            "request_id": kwargs['request_id']
        }
        kwargs.pop('action')
        kwargs.pop("request_id")
        serializer = await self.get_serializer(
            action_kwargs=action_kwargs,
            data=kwargs,
            context={"request": RequestImitator(self.account)}
        )
        serializer.is_valid(raise_exception=True)
        account_id = serializer.validated_data.get('account_id')
        if account_id == self.account_id:
            await self.send_json({"detail": "Other user required"})
        elif account_id is None:
            await self.send_json({"detail": "Account id is required."})
        else:
            try:
                account = await Account.objects.aget(pk=account_id)
            except Account.DoesNotExist:
                await self.send_json({"detail": "Account is not found"})
            else:
                if account in await self.all_accounts_chatting(self.account):
                    await self.send_json({"detail": "Chat already exists."})
                else:
                    chat = await self.save_serializer(serializer, members=[self.account, account])
                    last_message_serializer = await self.get_serializer(
                        action_kwargs={"action": "message_detail"},
                        instance=chat.last_message
                    )
                    await self.notify_users(chat, await self.get_serializer_data(last_message_serializer))

    @database_sync_to_async
    def all_accounts_chatting(self, account):
        members = []
        for ac in account.chats.all():
            for member in ac.members.all():
                if member != account:
                    members.append(member)
        return members

    @action()
    async def send_message(self, **kwargs):
        action_kwargs = {
            "action": kwargs['action'],
            "request_id": kwargs['request_id']
        }
        kwargs.pop('action')
        kwargs.pop("request_id")
        create_serializer = await self.get_serializer(
            action_kwargs=action_kwargs,
            data=kwargs,
            context={"request": RequestImitator(self.account)}
        )
        create_serializer.is_valid(raise_exception=True)
        content_object_model = message_types_models[create_serializer.validated_data.get('type')]
        content_object = await sync_to_async(content_object_model.objects.get)(
            id=create_serializer.validated_data.get('content_object')
        )
        message = await self.save_serializer(create_serializer)
        if message is None:
            await self.send_json({"detail": "You are not is the chat."})
        else:
            detail_serializer = await self.get_serializer(
                action_kwargs={
                    "request_id": action_kwargs['request_id'],
                    "action": "message_detail"
                },
                instance=message
            )
            data = await self.get_serializer_data(detail_serializer)
            await self.notify_users(chat_or_group=content_object, message_data=data)

    @database_sync_to_async
    def get_members(self, chat_or_group):
        return [m for m in chat_or_group.members.all()]

    async def notify_users(self, chat_or_group, message_data):
        members = await self.get_members(chat_or_group)
        for member in members:
            await self.channel_layer.group_send(
                str(member.id),
                {
                    "type": "update_messages",
                    "message": message_data
                }
            )

    async def update_messages(self, event):
        await self.send_json(event['message'])

    async def websocket_disconnect(self, message):
        await self.remove_group(self.account_id)
        await self.close()
