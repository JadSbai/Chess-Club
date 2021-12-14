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
            club_name = kwargs.get('club_name')
            target_user = request.user
            try:
                tournament = Tournament.objects.get(name=tournament_name)
            except ObjectDoesNotExist:
                messages.add_message(request, messages.ERROR, "The tournament you are looking for does not exist!")
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
            else:
                for perm in perms_list:
                    if not request.user.has_tournament_perm(perm, tournament):
                        if perm == 'chessclubs.withdraw':
                            generate_withdraw_messages(request, tournament, target_user)
                            return redirect('show_tournament', club_name=club_name, tournament_name=tournament_name)
                        elif perm == 'chessclubs.see_tournament_private_info':
                            messages.add_message(request, messages.WARNING,
                                                 "Permission denied! You have to be an Organiser or Co-organiser or Participant to see schedules")
                            return redirect('show_tournament', club_name=club_name, tournament_name=tournament_name)
                        else:
                            messages.add_message(request, messages.WARNING,
                                                 "Permission denied! You don't have the necessary tournament permission(s)")
                            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)


                return view_func(request, *args, **kwargs)

        return wrapped

    return wrapper


def generate_withdraw_messages(request, tournament, target_user):
    if tournament.is_organiser(target_user):
        messages.add_message(request, messages.WARNING,
                             "You are the organiser of this tournament. "
                             "You cannot apply and withdraw from your own tournaments.")
    else:
        messages.add_message(request, messages.WARNING,
                             "You are not a participant of this tournament.")


def must_be_non_participant(view_function):
    def modified_view_function(request, *args, **kwargs):
        tournament_name = kwargs.get('tournament_name')
        club_name = kwargs.get('club_name')
        target_user = request.user
        try:
            tournament = Tournament.objects.get(name=tournament_name)
        except ObjectDoesNotExist:
            messages.add_message(request, messages.ERROR, "The tournament you are looking for does not exist!")
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            if tournament.is_participant(target_user):
                messages.add_message(request, messages.WARNING, "You are already a participant.")
                return redirect('show_tournament', tournament_name=tournament_name, club_name=club_name)
            elif tournament.is_organiser(target_user):
                messages.add_message(request, messages.WARNING,
                                     "You are the organiser of this tournament. You cannot apply.")
                return redirect('show_tournament', tournament_name=tournament_name, club_name=club_name)
            elif tournament.is_co_organiser(target_user):
                messages.add_message(request, messages.WARNING,
                                     "You are a co-organiser of this tournament. You cannot apply.")
                return redirect('show_tournament', tournament_name=tournament_name, club_name=club_name)
            else:
                return view_function(request, *args, **kwargs)

    return modified_view_function
