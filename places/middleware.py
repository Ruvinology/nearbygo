import time
from urllib.parse import urlencode

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse

LAST_ACTIVITY_KEY = "nearbygo_admin_last_activity"


class AdminIdleTimeoutMiddleware:
    """
    Sign administrators out after a period of inactivity (NFR-SE-08).

    Visitors are not affected: the check only applies to authenticated staff
    accounts, and the timeout is set with ADMIN_IDLE_TIMEOUT (seconds).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated and user.is_staff:
            now = int(time.time())
            last = request.session.get(LAST_ACTIVITY_KEY)
            timeout = int(getattr(settings, "ADMIN_IDLE_TIMEOUT", 1800))
            if last is not None and now - int(last) > timeout:
                logout(request)
                if request.path.startswith(reverse("admin:index")):
                    messages.warning(request, "You were signed out after a period of inactivity. Please sign in again.")
                    return redirect(f"{reverse('admin:login')}?{urlencode({'next': request.path})}")
                # On public pages the visitor simply continues as a signed-out user.
                return self.get_response(request)
            request.session[LAST_ACTIVITY_KEY] = now
        return self.get_response(request)
