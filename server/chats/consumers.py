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
    GroupListSerializer, GroupCreateSerializer, GroupDetailSerializer,
    MessageDetailSerializer, MessageCreateSerializer,
)
from .models import Chat, get_messenger_object


class RequestImitator:
    def __init__(self, user):
        self.user = user


class ChatConsumer(ObserverModelInstanceMixin,
                   GenericAsyncAPIConsumer):
    queryset = Chat.objects.all()
    serializer_class = ChatListSerializer

    actions = {
        "chat_create": ChatCreateSerializer,
        "chat_list": ChatListSerializer,
        "chat_detail": ChatDetailSerializer,
        "group_create": GroupCreateSerializer,
        "group_list": GroupListSerializer,
        "group_detail": GroupDetailSerializer,
        "send_message": MessageCreateSerializer,
        "message_detail": MessageDetailSerializer
    }

    @database_sync_to_async
    def get_serializer(self, action_kwargs: dict | None = None, *args, **kwargs) -> Serializer:
        action_ = action_kwargs.get("action")
        if action_ not in self.actions:
            raise AssertionError(f"Please define action {action_}")
        serializer_class = self.actions[action_]
        return serializer_class(*args, **kwargs)

    @database_sync_to_async
    def get_serializer_data(self, serializer: Serializer) -> dict:
        return serializer.data

    @database_sync_to_async
    def save_serializer(self, serializer: Serializer, **kwargs):
        return serializer.save(**kwargs)

    async def websocket_connect(self, message):
        try:
            for permission in await self.get_permissions(action="connect"):
                if not await ensure_async(permission.can_connect)(
                        scope=self.scope, consumer=self, message=message
                ):
                    raise PermissionDenied()
            self.account = self.scope['user']
            if self.account is None:
                return
            await self.accept()
            self.account_id = str(self.account.id)
            await self.add_group(self.account_id)
        except PermissionDenied:
            await self.close()

    @action()
    async def chat_list(self, **kwargs):
        queryset = await sync_to_async(Chat.objects.all_account_chats)(self.account)
        serializer = await self.get_serializer(action_kwargs=kwargs, instance=queryset, many=True)
        await self.send_json(
            content=await self.get_serializer_data(serializer)
        )

    @action()
    async def chat_create(self, **kwargs):
        action_kwargs = self.prepare_data(**kwargs)
        serializer = await self.get_serializer(
            action_kwargs=action_kwargs,
            data=kwargs,
            context={"request": RequestImitator(self.account)}
        )
        serializer.is_valid(raise_exception=True)
        account_id = serializer.validated_data.get('account_id')
        if account_id == self.account_id:
            await self.send_json({"detail": "Other user required"})
        else:
            account = await sync_to_async(Account.objects.get)(pk=account_id)
            if account in await self.all_accounts_chatting(self.account):
                await self.send_json({"detail": "Chat already exists."})
            else:
                accounts = [self.account, account]
                chat = await self.save_serializer(serializer, members=accounts)
                last_message_serializer = await self.get_serializer(
                    action_kwargs={"action": "message_detail"},
                    instance=chat.last_message
                )
                await self.notify_accounts_by_list(
                    accounts=accounts,
                    data=await self.get_serializer_data(last_message_serializer)
                )

    @action()
    async def group_create(self, **kwargs):
        action_kwargs = self.prepare_data(**kwargs)
        serializer = await self.get_serializer(
            action_kwargs=action_kwargs,
            data=kwargs,
            context={"request": RequestImitator(self.account)}
        )
        serializer.is_valid(raise_exception=True)
        accounts_ids = [i['account_id'] for i in serializer.validated_data.get('accounts')]
        if self.account_id in accounts_ids:
            await self.send_json({"detail": "Other users required"})
        else:
            accounts = await self.get_accounts_by_ids(accounts_ids)
            if len(accounts) != len(accounts_ids):
                await self.send_json({"detail": "Some of users are not found."})
                return
            accounts.append(self.account)
            group = await self.save_serializer(serializer, members=accounts)
            group_detail_serializer = await self.get_serializer(
                action_kwargs={
                    "request_id": action_kwargs['request_id'],
                    "action": "group_detail"
                },
                instance=group
            )
            await self.notify_accounts_by_list(
                accounts=accounts,
                data=await self.get_serializer_data(group_detail_serializer)
            )

    @classmethod
    def prepare_data(cls, **kwargs) -> dict:
        action_kwargs = {
            "action": kwargs['action'],
            "request_id": kwargs['request_id']
        }
        kwargs.pop('action')
        kwargs.pop("request_id")
        return action_kwargs

    @action()
    async def send_message(self, **kwargs):
        action_kwargs = self.prepare_data(**kwargs)
        create_serializer = await self.get_serializer(
            action_kwargs=action_kwargs,
            data=kwargs,
            context={"request": RequestImitator(self.account)}
        )
        create_serializer.is_valid(raise_exception=True)
        content_object = await sync_to_async(get_messenger_object)(
            id_=create_serializer.validated_data.get('content_object'),
            type_=create_serializer.validated_data.get("type")
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
            await self.notify_accounts_by_chat_or_group(
                chat_or_group=content_object,
                data=data
            )

    @database_sync_to_async
    def get_members(self, chat_or_group):
        return [m for m in chat_or_group.members.all()]

    @database_sync_to_async
    def get_accounts_by_ids(self, ids: list):
        accounts = [
            account for account in
            Account.objects.filter(id__in=ids)
        ]
        return accounts

    async def notify_accounts_by_chat_or_group(self, chat_or_group, data):
        members = await self.get_members(chat_or_group)
        for member in members:
            await self.channel_layer.group_send(
                str(member.id),
                {
                    "type": "update_messages",
                    "message": data
                }
            )

    async def notify_accounts_by_list(self, accounts: list, data: dict):
        for account in accounts:
            await self.channel_layer.group_send(
                str(account.id),
                {
                    "type": "update_messages",
                    "message": data
                }
            )

    async def update_messages(self, event):
        await self.send_json(event['message'])

    async def websocket_disconnect(self, message):
        await self.remove_group(self.account_id)
        await self.close()
