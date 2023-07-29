from rest_framework.test import APIClient, APITestCase

from users.tests.fixtures import UserFixture
from chats.models import Chat, Message


class ChatFixture(UserFixture, APITestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
