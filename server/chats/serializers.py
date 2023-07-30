from django.core.files.base import ContentFile
from rest_framework import serializers
from uuid import uuid4

from .models import Chat, Message, MessageMedia, Group, message_types_models, message_types_choices
from users.serializers import AccountDetailSerializer


class MessageMediaCreateSerializer(serializers.ModelSerializer):
    media = serializers.CharField()

    class Meta:
        model = MessageMedia
        fields = ("media", "extension")


class MessageCreateSerializer(serializers.ModelSerializer):
    type = serializers.ChoiceField(choices=message_types_choices)
    account = serializers.HiddenField(default=serializers.CurrentUserDefault())
    medias = MessageMediaCreateSerializer(many=True)
    content_object = serializers.CharField()

    class Meta:
        model = Message
        fields = ("text", "account", "content_object", "source", "medias", "type")

    def save(self, **kwargs):
        kwargs.update(self.validated_data)
        content_object_model = message_types_models[kwargs['type']]
        content_object_id = kwargs.get('content_object')
        content_object = content_object_model.objects.get(id=content_object_id)
        message = content_object_model.objects.add_message(
            obj=content_object,
            text=kwargs.get("text"),
            account=kwargs.get("account"),
            source=kwargs.get("source"),
        )
        for media in kwargs.get('medias', []):
            extension = media.get('extension')
            name = f"{str(uuid4())}.{extension}" if extension is not None else f"{str(uuid4())}"
            file = ContentFile(media['media'].encode(), name=name)
            MessageMedia.objects.create(
                message=message,
                media=file,
                extension=media.get('extension')
            )
        return message


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
        message = Chat.objects.add_message(
            obj=chat,
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


class GroupCreateSerializer(serializers.ModelSerializer):
    account = serializers.HiddenField(default=serializers.CurrentUserDefault())
    message = MessageCreateSerializer()
    account_id = serializers.CharField()
    photo = serializers.CharField()
    is_public = serializers.BooleanField(default=True)

    class Meta:
        model = Group
        fields = ("account_id", "message", "account", "photo", "is_public")

    def save(self, **kwargs):
        kwargs.update(self.validated_data)
        kwargs.pop("account_id")
        photo = kwargs.get("photo")
        if photo is not None:
            photo = ContentFile(photo.encode(), name=f"{str(uuid4())}.png")
        group = self.Meta.model.objects.create_group(
            members=kwargs['members'],
            title=kwargs['title'],
            photo=photo,
            is_public=kwargs['is_public']
        )
        message = Group.objects.add_message(
            obj=group,
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
        return group


class GroupListSerializer(serializers.ModelSerializer):
    messages = MessageListSerializer(many=True)

    class Meta:
        model = Group
        fields = (
            "id",
            "get_photo_url",
            "title",

        )


class GroupDetailSerializer(serializers.ModelSerializer):
    messages = MessageDetailSerializer(many=True)
    owner = AccountDetailSerializer(read_only=True)
    members = AccountDetailSerializer(many=True)

    class Meta:
        model = Group
        fields = (
            "id",
            "members",
            "messages",
            "get_photo_url",
            'is_public',
            "title",
            "owner",
            "time_created",

        )
