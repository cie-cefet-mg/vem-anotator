"""
Optional middleware that requires a session unlock before accessing the annotation app.

The Django admin (/admin/) is excluded so this simple gate does not interfere with it.
"""
from urllib.parse import urlencode

from django.conf import settings
from django.shortcuts import redirect


class SiteAccessMiddleware:
    """Redirects to /login/ when the gate is enabled and the session is not unlocked."""

    SESSION_KEY = "site_access_ok"

    # Paths that bypass session verification (login, static files, admin).
    EXEMPT_PREFIXES = (
        "/login/",
        "/static/",
        "/admin/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not getattr(settings, "SITE_ACCESS_ENABLED", False):
            return self.get_response(request)

        path = request.path
        if any(path.startswith(p) for p in self.EXEMPT_PREFIXES):
            return self.get_response(request)

        if request.session.get(self.SESSION_KEY):
            return self.get_response(request)

        login_path = getattr(settings, "SITE_ACCESS_LOGIN_PATH", "/login/")
        query = urlencode({"next": request.get_full_path()})
        return redirect(f"{login_path}?{query}")
