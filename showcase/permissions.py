from rest_framework.permissions import BasePermission
from django.conf import settings


class InternalSyncTokenPermission(BasePermission):
    """内部同步接口 Bearer Token 鉴权"""

    def has_permission(self, request, view):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith("Bearer "):
            return False
        token = auth_header[7:]
        expected_token = getattr(settings, "INTERNAL_SYNC_TOKEN", "")
        if not expected_token:
            return False
        return token == expected_token
