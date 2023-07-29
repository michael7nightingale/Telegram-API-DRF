from rest_framework.test import APITestCase

from .fixtures import ChatFixture


class TestChatView(ChatFixture, APITestCase):
    pass
