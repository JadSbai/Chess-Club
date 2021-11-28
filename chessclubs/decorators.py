from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from .models import Club

def login_prohibited(view_function):
    def modified_view_function(request):
        if request.user.is_authenticated:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request)

    return modified_view_function


def club_permission_required(perm):
    def wrapper(view_func):
        def wrapped(request, *args, **kwargs):
            club_name = kwargs.get('club_name')
            club = Club.objects.get(name=club_name)
            if not request.user.has_club_perm(perm, club):
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
            else:
                return view_func(request, *args, **kwargs)
        return wrapped
    return wrapper
