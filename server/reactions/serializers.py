from rest_framework import serializers

from .models import Reaction, ReactionItem


class ReactionItemListSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReactionItem
        fields = ("id", "get_image_path", "name")


class ReactionListSerializer(serializers.ModelSerializer):
    reaction_item = ReactionItemListSerializer(read_only=True)

    class Meta:
        model = Reaction
        fields = ("reaction_item", "account", "id")


class ReactionCreateSerializer(serializers.ModelSerializer):
    account = serializers.HiddenField(default=serializers.CurrentUserDefault())
    reaction_item_id = serializers.CharField(source="reaction_item__id")
    message_id = serializers.CharField(source="message__id")

    class Meta:
        model = Reaction
        fields = ("account", "reaction_item_id", "message_id")
