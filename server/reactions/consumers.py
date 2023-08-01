from rest_framework.serializers import Serializer
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.observer.generics import ObserverModelInstanceMixin
from channels.db import database_sync_to_async

from .serializers import ReactionListSerializer, ReactionCreateSerializer


class ReactionConsumeMixin(ObserverModelInstanceMixin,
                           GenericAsyncAPIConsumer):
    reactions_actions = {
        "reaction_create": ReactionCreateSerializer,
        "reaction_list": ReactionListSerializer,

    }

    @database_sync_to_async
    def get_reaction_serializer(self, action_kwargs: dict | None = None, *args, **kwargs) -> Serializer:
        action_ = action_kwargs.get("action")
        if action_ not in self.reactions_actions:
            raise AssertionError(f"Please define action {action_}")
        serializer_class = self.reactions_actions[action_]
        return serializer_class(*args, **kwargs)
