from rest_framework.test import APITestCase
from django.urls import reverse

from .fixtures import ChatFixture


class TestChatView(ChatFixture, APITestCase):

    def test_chat_create(self):
        data = {
            "account_id": self.account2.id,
            "message": {
                "text": "Hello, man"
            }
        }

