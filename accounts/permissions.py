from functools import wraps
from django.http import HttpResponseForbidden

from .models import UserProfile


def is_org_admin(user):
    """Superuser or profile role admin sees all visitors / full queue."""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    role = getattr(getattr(user, "profile", None), "role", None)
    return role == UserProfile.ROLE_ADMIN


def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Login required")
            role = getattr(getattr(request.user, "profile", None), "role", None)
            if request.user.is_superuser or role in allowed_roles:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("Access denied")

        return _wrapped

    return decorator
