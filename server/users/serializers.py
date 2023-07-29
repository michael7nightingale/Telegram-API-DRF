from rest_framework import serializers

from .models import Account


class AccountCreateSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ("username", "phone_number", "first_name", "last_name", "password")
        model = Account


class AccountDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",

        )
