from django.db import models
from enum import StrEnum


class ReactionSignalEnum(StrEnum):
    created = "created"
    deleted = "deleted"
    new_item = "new_reaction"


class ReactionManager(models.Manager):
    def create_reaction(self, account, message, reaction_item):
        reaction = self.get(account=account, message=message)
        if reaction is not None:
            if reaction.reaction_item == reaction_item:
                reaction.delete()
                return reaction, ReactionSignalEnum.deleted
            else:
                reaction.reaction_item = reaction_item
                reaction.save()
                return reaction, ReactionSignalEnum.new_item

        new_reaction = Reaction.objects.create(
            account=account,
            message=message,
            reaction_item=reaction_item
        )
        return new_reaction, ReactionSignalEnum.created

    def all_by_message(self, message):
        return self.filter(message=message)


class Reaction(models.Model):
    message = models.ForeignKey("chats.Message", on_delete=models.CASCADE, verbose_name="reactions")
    reaction_item = models.ForeignKey("ReactionItem", on_delete=models.CASCADE)
    account = models.ForeignKey("users.Account", on_delete=models.CASCADE)

    objects = ReactionManager()

    class Meta:
        unique_together = ("account", "message", "reaction_item")


class ReactionItem(models.Model):
    name = models.CharField("Item name", max_length=100, unique=True)
    image = models.ImageField("Reaction image", upload_to="reaction_items/")

    def get_image_url(self) -> str:
        return self.image.url
