from django.db import models


class Reaction(models.Model):
    message = models.ForeignKey("chats.Message", on_delete=models.CASCADE, verbose_name="reactions")
    reaction_item = models.ForeignKey("ReactionItem", on_delete=models.CASCADE)
    account = models.ForeignKey("users.Account", on_delete=models.CASCADE)


class ReactionItem(models.Model):
    name = models.CharField("Item name", max_length=100, unique=True)
    image = models.ImageField("Reaction image", upload_to="reaction_items/")

    def get_image_url(self) -> str:
        return self.image.url
