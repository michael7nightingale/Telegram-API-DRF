from rest_framework import serializers

from .models import Chat, Message
from users.serializers import AccountDetailSerializer


class MessageCreateSerializer(serializers.ModelSerializer):
    account = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Message
        fields = ("account", "text", "content_object", "source")


class MessageDetailSerializer(serializers.ModelSerializer):
    account = AccountDetailSerializer(read_only=True)

    class Meta:
        model = Message
        fields = (
            "account",
            "text",
            "time_send",
            "time_update",

        )


class MessageListSerializer(serializers.ModelSerializer):
    account = AccountDetailSerializer(read_only=True)

    class Meta:
        model = Message
        fields = (
            "account",
            "text",
            "source",

        )


class ChatCreateSerializer(serializers.ModelSerializer):
    account = serializers.HiddenField(default=serializers.CurrentUserDefault())
    message = MessageCreateSerializer()
    account_id = serializers.CharField()

    class Meta:
        model = Chat
        fields = ("account_id", "message", "account")

    def save(self, **kwargs):
        kwargs.update(self.validated_data)
        kwargs.pop("account_id")
        chat = self.Meta.model.objects.create_chat(kwargs['members'])
        Chat.objects.add_message(
            chat=chat,
            account=kwargs['message']['account'],
            text=kwargs['message']['text'],
            source=kwargs['message'].get('source')
        )

        return chat


class ChatListSerializer(serializers.ModelSerializer):
    messages = MessageListSerializer(many=True)

    class Meta:
        model = Chat
        fields = ("id", "members", "messages")


class ChatDetailSerializer(serializers.ModelSerializer):
    messages = MessageDetailSerializer(many=True)

    class Meta:
        model = Chat
        fields = (
            "id",
            "members",
            "messages",

        )
