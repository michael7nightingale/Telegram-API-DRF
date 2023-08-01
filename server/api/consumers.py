from rest_framework.serializers import Serializer
from rest_framework.exceptions import PermissionDenied
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.observer.generics import ObserverModelInstanceMixin
from djangochannelsrestframework.scope_utils import ensure_async
from channels.db import database_sync_to_async

from chats.consumers import ChatConsumerMixin, GroupConsumerMixin, MessageConsumerMixin
from users.models import Account


class ChatConsumer(
    ChatConsumerMixin,
    GroupConsumerMixin,
    MessageConsumerMixin,
    ObserverModelInstanceMixin,
    GenericAsyncAPIConsumer
):
    @database_sync_to_async
    def get_serializer(self, action_kwargs: dict | None = None, *args, **kwargs) -> Serializer:
        return Serializer(*args, **kwargs)

    @database_sync_to_async
    def get_serializer_data(self, serializer: Serializer) -> dict:
        return serializer.data

    @database_sync_to_async
    def save_serializer(self, serializer: Serializer, **kwargs):
        return serializer.save(**kwargs)

    @database_sync_to_async
    def update_serializer(self, serializer: Serializer, *args, **kwargs):
        return serializer.update(*args, **kwargs)

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

    @classmethod
    def prepare_data(cls, **kwargs) -> dict:
        action_kwargs = {
            "action": kwargs['action'],
            "request_id": kwargs['request_id']
        }
        kwargs.pop('action')
        kwargs.pop("request_id")
        return action_kwargs

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
