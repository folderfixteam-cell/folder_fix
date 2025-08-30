from functools import wraps
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

def membership_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        m = getattr(request.user, "membership", None)
        if not m or not m.is_active():
            return redirect("accounts:dashboard")
        return view_func(request, *args, **kwargs)
    return _wrapped
