from http import HTTPStatus

from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Account
from .serializers import AccountCreateSerializer


class AccountViewSet(mixins.CreateModelMixin,
                     viewsets.GenericViewSet):
    queryset = Account.objects.all()
    lookup_url_kwarg = "username"
    lookup_field = "username"

    def get_permissions(self):
        if self.action in ("create", ):
            pc = [AllowAny]
        else:
            pc = [IsAuthenticated]
        return [p() for p in pc]

    def get_serializer(self, *args, **kwargs):
        match self.action:
            case "create":
                s = AccountCreateSerializer
            case _:
                s = AccountCreateSerializer
        return s(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        Account.objects.create_user(**serializer.validated_data)
        return Response(serializer.validated_data, status=HTTPStatus.OK)
