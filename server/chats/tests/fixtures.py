from rest_framework.test import APITestCase

from users.tests.fixtures import UserFixture


class ChatFixture(UserFixture, APITestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
