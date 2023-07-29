from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation


class ChatManager(models.Manager):
    pass

    def get(self, *args, **kwargs):
        return (
            super()
            .prefetch_related("messages", "members", "messages__account")
            .get(*args, **kwargs)
        )

    def filter(self, **kwargs):
        return (
            super()
            .prefetch_related("messages", "members", "messages__account")
            .filter(**kwargs)
        )

    def all(self):
        return (
            super()
            .prefetch_related("messages", "members", "messages__account")
            .all()
        )

    def create_chat(self, members: list):
        chat = Chat()
        chat.save()
        chat.members.add(*members)
        return chat

    def add_message(self, chat, text: str, account, source):
        if chat.members.filter(id=account.id).exists():
            message = Message(
                content_object=chat,
                text=text,
                account=account,
                source=source
            )
            message.save()
            chat.last_message = message
            chat.save()
        else:
            return None

    def all_account_chats(self, account):
        return account.chats.all()


class Chat(models.Model):
    members = models.ManyToManyField(
        "users.Account",
        verbose_name="Members",
        related_name="chats"
    )
    messages = GenericRelation("Message", object_id_field="id")
    last_message = models.OneToOneField("Message", on_delete=models.SET_NULL, null=True, blank=True)

    objects = ChatManager()


class Group(models.Model):
    members = models.ManyToManyField(
        "users.Account",
        verbose_name="Members",
        related_name="group_chats"
    )
    is_public = models.BooleanField(default=True)
    time_created = models.DateTimeField(auto_created=True)
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(
        to="users.Account",
        on_delete=models.CASCADE,
        related_name="own_groups"
    )

    messages = GenericRelation("Message")

    objects = ChatManager()


class MessageManager(models.Manager):
    # def get(self, *args, **kwargs):
    #     return (
    #         super()
    #         .select_related("account")
    #         .get(*args, **kwargs)
    #     )
    #
    # def filter(self, **kwargs):
    #     return (
    #         super()
    #         .select_related("account")
    #         .filter(**kwargs)
    #     )
    #
    # def all(self):
    #     return (
    #         super()
    #         .select_related("account")
    #         .all()
    #     )

    pass


class Message(models.Model):
    content_object = GenericForeignKey(ct_field="content_type", fk_field="id")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    account = models.ForeignKey("users.Account", on_delete=models.CASCADE)
    text = models.TextField(max_length=2000, null=True)
    source = models.ForeignKey(
        to="self",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    viewed = models.BooleanField(default=False)

    time_send = models.DateTimeField("Time send", auto_created=True, auto_now=True)
    time_update = models.DateTimeField("Time update", null=True, auto_now_add=True)

    objects = MessageManager()

    def __str__(self):
        return self.text


def media_upload_to(odj):
    return f"uploads/{odj.id}"


class MessageMedia(models.Model):
    media = models.FileField("Media", upload_to=media_upload_to)
    message = models.ForeignKey("Message", on_delete=models.CASCADE)

    objects = models.Manager()
