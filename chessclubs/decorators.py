from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from .models import Club, User
from django.contrib import messages

def login_prohibited(view_function):
    def modified_view_function(request):
        if request.user.is_authenticated:
            messages.add_message(request, messages.WARNING, "You need to log out first!")
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
                messages.add_message(request, messages.WARNING, "Permission denied!")
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
            else:
                return view_func(request, *args, **kwargs)
        return wrapped
    return wrapper

def add_current_user_to_logged_in_group(club):
    for user in User.objects.all():
        if club.owner != user:
            club.add_to_logged_in_non_members_group(user)