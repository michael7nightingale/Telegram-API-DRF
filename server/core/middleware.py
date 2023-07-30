from urllib.parse import parse_qs
from typing import Optional
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import PermissionDenied

from users.models import Account
from channels.db import database_sync_to_async


@database_sync_to_async
def get_user_from_db(token: str) -> Optional[Account]:
    """Get user by its user_id."""
    try:
        token = Token.objects.get(key=token)
        return Account.objects.get(pk=token.user_id)    # type: ignore
    except Account.DoesNotExist:
        return None


class TokenAuthMiddleware:
    """Token authentication middleware for channels."""
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query_string = scope['query_string'].decode()
        query_string_parse = parse_qs(query_string)
        if "token" not in query_string_parse:
            raise PermissionDenied("Authentication credentials are not provided.")
        token = query_string_parse['token'][0]
        user = await get_user_from_db(token)
        scope['user'] = user
        return await self.app(scope, receive, send)
