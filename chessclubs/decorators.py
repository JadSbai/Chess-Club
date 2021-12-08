from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from .models import Club, Tournament
from django.contrib import messages


def login_prohibited(view_function):
    def modified_view_function(request):
        if request.user.is_authenticated:
            messages.add_message(request, messages.WARNING, "You need to log out first!")
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request)

    return modified_view_function


def club_permissions_required(perms_list):
    def wrapper(view_func):
        def wrapped(request, *args, **kwargs):
            club_name = kwargs.get('club_name')
            try:
                club = Club.objects.get(name=club_name)
            except ObjectDoesNotExist:
                messages.add_message(request, messages.ERROR, "The club you are looking for does not exist!")
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
            else:
                for perm in perms_list:
                    if not request.user.has_club_perm(perm, club):
                        messages.add_message(request, messages.WARNING,
                                             "Permission denied! You don't have the necessary club permission(s)")
                        return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
                return view_func(request, *args, **kwargs)
        return wrapped
    return wrapper


def tournament_permissions_required(perms_list):
    def wrapper(view_func):
        def wrapped(request, *args, **kwargs):
            tournament_name = kwargs.get('tournament_name')
            try:
                tournament = Tournament.objects.get(name=tournament_name)
            except ObjectDoesNotExist:
                messages.add_message(request, messages.ERROR, "The tournament you are looking for does not exist!")
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
            else:
                for perm in perms_list:
                    if not request.user.has_tournament_perm(perm, tournament):
                        messages.add_message(request, messages.WARNING,
                                             "Permission denied! You don't have the necessary tournament permission(s)")
                        return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)

                return view_func(request, *args, **kwargs)
        return wrapped
    return wrapper



