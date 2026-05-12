from functools import wraps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            profile = getattr(request.user, "profile", None)
            if request.user.is_superuser or (profile and profile.role in roles):
                return view_func(request, *args, **kwargs)
            messages.error(request, "You do not have permission to access that page.")
            return redirect("dashboard")

        return wrapper

    return decorator


def instructor_required(view_func):
    return role_required("instructor", "admin")(view_func)
