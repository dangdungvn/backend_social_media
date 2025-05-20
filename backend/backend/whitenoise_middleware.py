"""
ASGI Static Files Middleware cho Django Channels
"""

import os
import posixpath
import stat
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.staticfiles.handlers import StaticFilesHandler
from django.core.asgi import get_asgi_application


class ASGIStaticFilesHandler:
    """
    ASGI middleware để phục vụ static files.
    """

    def __init__(self, app):
        self.app = app
        self.base_url = settings.STATIC_URL
        self.base_dir = settings.STATIC_ROOT
        self.media_url = settings.MEDIA_URL
        self.media_dir = settings.MEDIA_ROOT

    async def __call__(self, scope, receive, send):
        """
        ASGI application để xử lý request.
        """
        # Kiểm tra nếu là HTTP request cho static files
        if scope["type"] == "http":
            path = scope["path"]

            # Nếu path bắt đầu với STATIC_URL hoặc MEDIA_URL
            if path.startswith(self.base_url) or path.startswith(self.media_url):
                # Sử dụng Django ASGI app để phục vụ static files
                django_app = get_asgi_application()
                return await django_app(scope, receive, send)

        # Nếu không phải static/media, chuyển đến app tiếp theo
        return await self.app(scope, receive, send)
