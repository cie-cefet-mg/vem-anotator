"""Template globals related to the access gate."""
from django.conf import settings


def site_access(request):
    """
    Exposes flags for base.html, such as a logout button, without polluting each view.
    """
    enabled = getattr(settings, "SITE_ACCESS_ENABLED", False)
    key = "site_access_ok"
    logged = bool(enabled and request.session.get(key))
    expects_username = bool(getattr(settings, "SITE_ACCESS_USERNAME", "") or "")
    return {
        "site_access_active": enabled,
        "site_access_in": logged,
        "site_access_expects_username": expects_username,
    }
