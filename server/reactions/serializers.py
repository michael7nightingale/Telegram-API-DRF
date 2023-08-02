from rest_framework import serializers
from rest_framework.exceptions import NotFound

from chats.models import Message
from users.serializers import AccountDetailSerializer
from .models import Reaction, ReactionItem


class ReactionItemListSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReactionItem
        fields = ("id", "get_image_path", "name")


class ReactionListSerializer(serializers.ModelSerializer):
    reaction_item = ReactionItemListSerializer(read_only=True)

    class Meta:
        model = Reaction
        fields = ("reaction_item", "account", "id", "message__id")


class ReactionDetailSerializer(serializers.ModelSerializer):
    reaction_item = ReactionItemListSerializer(read_only=True)
    account = AccountDetailSerializer(read_only=True)

    class Meta:
        model = Reaction
        fields = ("reaction_item", "account", "id", "message__id")


class ReactionCreateSerializer(serializers.ModelSerializer):
    account = serializers.HiddenField(default=serializers.CurrentUserDefault())
    reaction_item_id = serializers.CharField(source="reaction_item__id")
    message_id = serializers.CharField(source="message__id")

    class Meta:
        model = Reaction
        fields = ("account", "reaction_item_id", "message_id")

    def save(self, **kwargs):
        kwargs.update(self.validated_data)
        reaction_item = ReactionItem.objects.get(id=kwargs['reaction_item_id'])
        if reaction_item is None:
            raise NotFound()
        message = Message.objects.get(id=kwargs['message_id'])
        if message is None:
            raise NotFound()
        Message.objects.check_member_permissions(message.content_object, kwargs['account'])
        reaction, signal = Reaction.objects.create_reaction(
            account=kwargs['account'],
            reaction_item=reaction_item,
            message=message
        )
        return reaction, signal


class ReactionListRequestSerializer(serializers.Serializer):
    message_id = serializers.CharField()
