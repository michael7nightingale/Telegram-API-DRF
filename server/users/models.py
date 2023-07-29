from django.contrib.auth.hashers import make_password
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager


class AccountManager(UserManager):
    def create_user(
            self,
            username: str,
            phone_number: str,
            password: str,
            first_name: str,
            last_name: str
    ):
        username = Account.normalize_username(username)
        user = self.model(
            username=username,
            phone_number=phone_number,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
            self,
            phone_number: str,
            password: str,
            username: str | None = None,
            first_name: str | None = None,
            last_name: str | None = None,
    ):
        user = self.model(
            username=username,
            phone_number=phone_number,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_superuser=True
        )
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    # def get(self, *args, **kwargs):
    #     return (
    #         super()
    #         .prefetch_related("chats")
    #         .get(*args, **kwargs)
    #     )
    #
    # def filter(self, **kwargs):
    #     return (
    #         super()
    #         .prefetch_related("chats")
    #         .filter(**kwargs)
    #     )
    #
    # def all(self):
    #     return (
    #         super()
    #         .prefetch_related("chats")
    #         .all()
    #     )


class Account(AbstractUser):
    email = None
    username = models.CharField("Username", max_length=100, unique=True)
    first_name = models.CharField("First name", max_length=100)
    last_name = models.CharField("Last name", max_length=100)
    phone_number = models.CharField("Phone number", max_length=20, unique=True)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    objects = AccountManager()

    def __str__(self):
        return f"@{self.username}"

    class Meta:
        unique_together = ("username", "phone_number")
