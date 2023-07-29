from rest_framework.test import APIClient, APITestCase

from users.models import Account


class UserFixture(APITestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.account1 = Account.objects.create_user(
            username="michael7",
            password="password",
            phone_number="8907829123",
            first_name="Michael",
            last_name="Nightingale"
        )
        cls.client1 = APIClient()
        cls.client1.force_login(cls.client1)

        cls.account2 = Account.objects.create_user(
            username="michael7123",
            password="passwor123d",
            phone_number="82907829223",
            first_name="Micha123el",
            last_name="N123ightingale"
        )
        cls.client2 = APIClient()
        cls.client2.force_login(cls.client2)

        cls.account3 = Account.objects.create_user(
            username="michae123l7133",
            password="passwo123r133d",
            phone_number="839207839333",
            first_name="Micha4133el",
            last_name="N133ig4htingale"
        )
        cls.client3 = APIClient()
        cls.client3.force_login(cls.client3)
