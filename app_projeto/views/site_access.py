"""
Views for the site access gate (password configured through environment variables, not in code).

Password comparison uses hmac.compare_digest to reduce timing leakage.
"""
import hmac

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from app_projeto.middleware import SiteAccessMiddleware


def _passwords_match(received: str, expected: str) -> bool:
    """Compares passwords in near-constant time to reduce basic timing leakage."""
    if not received or not expected:
        return False
    try:
        return hmac.compare_digest(received.encode("utf-8"), expected.encode("utf-8"))
    except (TypeError, ValueError, AttributeError):
        return False


def site_access_login(request):
    """
    Single gate screen: if SITE_ACCESS_ENABLED is false, send the user straight to the home page.
    """
    if not getattr(settings, "SITE_ACCESS_ENABLED", False):
        return HttpResponseRedirect(reverse("app_projeto:home"))

    if request.session.get(SiteAccessMiddleware.SESSION_KEY):
        return HttpResponseRedirect(_safe_next(request) or reverse("app_projeto:home"))

    if request.method == "POST":
        password = (request.POST.get("password") or "").strip()
        username = (request.POST.get("username") or "").strip()
        expected_user = getattr(settings, "SITE_ACCESS_USERNAME", "") or ""
        expected_pass = getattr(settings, "SITE_ACCESS_PASSWORD", "") or ""

        user_ok = True
        if expected_user:
            # The gate username does not need compare_digest because it is not secret like the password.
            user_ok = username == expected_user

        if user_ok and _passwords_match(password, expected_pass):
            request.session[SiteAccessMiddleware.SESSION_KEY] = True
            return HttpResponseRedirect(_safe_next(request) or reverse("app_projeto:home"))

        messages.error(request, "Incorrect username or password.")

    next_url = request.POST.get("next") if request.method == "POST" else request.GET.get("next")
    next_url = next_url or ""
    return render(request, "site_access_login.html", {"next_url": next_url})


def site_access_logout(request):
    """Closes only the gate; it does not log the user out of Django admin."""
    request.session.pop(SiteAccessMiddleware.SESSION_KEY, None)
    messages.info(request, "You have exited the annotator access gate.")
    return HttpResponseRedirect(reverse("app_projeto:site_access_login_en"))


def _safe_next(request) -> str | None:
    """Prevents open redirects to external domains."""
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return None
