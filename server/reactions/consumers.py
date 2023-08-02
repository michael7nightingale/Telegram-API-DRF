from asgiref.sync import sync_to_async
from rest_framework.serializers import Serializer
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.observer.generics import ObserverModelInstanceMixin
from djangochannelsrestframework.decorators import action
from channels.db import database_sync_to_async

from chats.models import Message
from .models import Reaction
from .serializers import (
    ReactionListSerializer,
    ReactionCreateSerializer,
    ReactionDetailSerializer,
    ReactionListRequestSerializer,

)


class ReactionConsumerMixin(ObserverModelInstanceMixin,
                           GenericAsyncAPIConsumer):
    reactions_actions = {
        "reaction_create": ReactionCreateSerializer,
        "reaction_list": ReactionListSerializer,
        "reaction_detail": ReactionDetailSerializer,
        "reaction_request_list": ReactionListRequestSerializer,

    }

    @database_sync_to_async
    def get_reaction_serializer(self, action_kwargs: dict | None = None, *args, **kwargs) -> Serializer:
        action_ = action_kwargs.get("action")
        if action_ not in self.reactions_actions:
            raise AssertionError(f"Please define action {action_}")
        serializer_class = self.reactions_actions[action_]
        return serializer_class(*args, **kwargs)

    @action()
    async def reaction_create(self, **kwargs):
        action_kwargs = self.prepare_data(**kwargs)
        create_serializer = await self.get_reaction_serializer(
            action_kwargs=action_kwargs,
            data=kwargs,
            context={"request": await self.imitate_request(user=self.account)}
        )
        create_serializer.is_valid(raise_exception=True)
        reaction, signal = create_serializer.save()
        detail_serializer = await self.get_reaction_serializer(
            action_kwargs={
                "request_id": action_kwargs['request_id'],
                "action": "reaction_detail"
            },
            instance=reaction
        )
        data = await self.get_serializer_data(detail_serializer)
        data['signal'] = signal
        await self.notify_accounts_by_chat_or_group(
            chat_or_group=reaction.message.content_object,
            data=data
        )

    @action()
    async def reaction_list(self, **kwargs):
        action_kwargs = self.prepare_data(**kwargs)
        request_list_serializer = await self.get_reaction_serializer(
            action_kwargs={
                "request_id": action_kwargs['request_id'],
                "action": "reaction_request_list"
            },
            data=kwargs,
        )
        request_list_serializer.is_valid(raise_exception=True)
        message = await sync_to_async(Message.objects.get)(id=request_list_serializer.validated_data['message_id'])
        detail_serializer = await self.get_reaction_serializer(
            action_kwargs=action_kwargs,
            instance=Reaction.objects.all_by_message(message)
        )
        data = await self.get_serializer_data(detail_serializer)
        await self.send_json(data)
