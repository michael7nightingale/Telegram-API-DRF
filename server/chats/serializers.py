from uuid import uuid4

from django.core.files import File
from django.core.files.base import ContentFile
from rest_framework import serializers

from .models import Chat, Message, MessageMedia
from users.serializers import AccountDetailSerializer


class MessageMediaCreateSerializer(serializers.ModelSerializer):
    media = serializers.CharField()

    class Meta:
        model = MessageMedia
        fields = ("media", "extension")


class MessageCreateSerializer(serializers.ModelSerializer):
    account = serializers.HiddenField(default=serializers.CurrentUserDefault())
    medias = MessageMediaCreateSerializer(many=True)

    class Meta:
        model = Message
        fields = ("text", "account", "content_object", "source", "medias")


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
        message = Message.objects.create(
            content_object=chat,
            account=kwargs['message']['account'],
            text=kwargs['message']['text'],
            source=kwargs['message'].get('source')
        )
        for media in kwargs['message'].get('medias'):
            extension = media.get('extension')
            name = f"{str(uuid4())}.{extension}" if extension is not None else f"{str(uuid4())}"
            file = ContentFile(media['media'].encode(), name=name)
            MessageMedia.objects.create(
                message=message,
                media=file,
                extension=media.get('extension')
            )

        Chat.objects.add_message_instance(chat, message)

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
