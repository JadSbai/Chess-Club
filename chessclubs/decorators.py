from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from .models import Club, Tournament, User, Match
from django.contrib import messages
from django.utils import timezone


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
                club = Club.objects.get(name=club_name)
            except ObjectDoesNotExist:
                messages.add_message(request, messages.ERROR, "The club you are looking for does not exist!")
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
            try:
                tournament = Tournament.objects.get(name=tournament_name)
            except ObjectDoesNotExist:
                messages.add_message(request, messages.ERROR, "The tournament you are looking for does not exist!")
                return redirect('show_club', club_name=club_name)
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
                        elif perm == 'chessclubs.add_co_organiser':
                            messages.add_message(request, messages.WARNING,
                                                 "You can only assign officers as co_organisers of your tournament")
                            return redirect('show_tournament', club_name=club_name, tournament_name=tournament_name)
                        elif perm == 'chessclubs.enter_match_results':
                            messages.add_message(request, messages.WARNING,
                                                 "Only the organiser and co-organisers can enter results")
                            return redirect('show_schedule', club_name=club_name, tournament_name=tournament_name)
                        elif perm == 'chessclubs.publish_schedule':
                            messages.add_message(request, messages.WARNING,
                                                 "Only the organiser can publish the schedule")
                            return redirect('show_tournament', club_name=club_name, tournament_name=tournament_name)
                        elif perm == 'chessclubs.start_tournament':
                            messages.add_message(request, messages.WARNING,
                                                 "Only the organiser can start the tournament")
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
            return redirect('show_club', club_name=club_name)
        else:
            if tournament.is_participant(target_user):
                messages.add_message(request, messages.WARNING, "You are already a participant.")
                return redirect('show_tournament', tournament_name=tournament_name, club_name=club_name)
            elif tournament.is_organiser(target_user):
                messages.add_message(request, messages.WARNING,
                                     "You are the organiser of this tournament. You cannot join.")
                return redirect('show_tournament', tournament_name=tournament_name, club_name=club_name)
            elif tournament.is_co_organiser(target_user):
                messages.add_message(request, messages.WARNING,
                                     "You are a co-organiser of this tournament. You cannot join.")
                return redirect('show_tournament', tournament_name=tournament_name, club_name=club_name)
            else:
                return view_function(request, *args, **kwargs)

    return modified_view_function


def deadline_must_not_be_passed(view_function):
    def modified_view_function(request, *args, **kwargs):
        tournament_name = kwargs.get('tournament_name')
        tournament = Tournament.objects.get(name=tournament_name)
        club_name = kwargs.get('club_name')
        if tournament.deadline <= timezone.now():
            messages.add_message(request, messages.WARNING,
                                 "The deadline is already passed! You can't join or withdraw.")
            return redirect('show_tournament', tournament_name=tournament_name, club_name=club_name)
        else:
            return view_function(request, *args, **kwargs)

    return modified_view_function


def deadline_must_be_passed(view_function):
    def modified_view_function(request, *args, **kwargs):
        tournament_name = kwargs.get('tournament_name')
        tournament = Tournament.objects.get(name=tournament_name)
        club_name = kwargs.get('club_name')
        if tournament.deadline > timezone.now():
            messages.add_message(request, messages.WARNING,
                                 "The deadline is not yet passed!")
            return redirect('show_tournament', tournament_name=tournament_name, club_name=club_name)
        else:
            return view_function(request, *args, **kwargs)

    return modified_view_function


def tournament_must_be_published(view_function):
    def modified_view_function(request, *args, **kwargs):
        tournament_name = kwargs.get('tournament_name')
        tournament = Tournament.objects.get(name=tournament_name)
        club_name = kwargs.get('club_name')
        if not tournament.is_published():
            messages.add_message(request, messages.WARNING, "The schedule hasn't been published yet")
            return redirect('show_tournament', tournament_name=tournament_name, club_name=club_name)
        else:
            return view_function(request, *args, **kwargs)

    return modified_view_function


def target_user_must_be_officer(view_function):
    def modified_view_function(request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        club_name = kwargs.get('club_name')
        tournament_name = kwargs.get('tournament_name')
        try:
            user = User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            messages.add_message(request, messages.ERROR, "The officer you are looking for doesn't exist")
            return redirect('show_tournament', tournament_name=tournament_name, club_name=club_name)
        else:
            club = Club.objects.get(name=club_name)
            if club.user_status(user) != "officer":
                messages.add_message(request, messages.WARNING, "You can only add officers as co_organisers")
                return redirect('show_tournament', tournament_name=tournament_name, club_name=club_name)
            else:
                return view_function(request, *args, **kwargs)

    return modified_view_function


def match_must_be_in_tournament(view_function):
    def modified_view_function(request, *args, **kwargs):
        match_id = kwargs.get('match_id')
        club_name = kwargs.get('club_name')
        tournament_name = kwargs.get('tournament_name')
        try:
            match = Match.objects.get(id=match_id)
        except ObjectDoesNotExist:
            messages.add_message(request, messages.ERROR, "The match you are looking for doesn't exist")
            return redirect('show_schedule', tournament_name=tournament_name, club_name=club_name)
        else:
            tournament = Tournament.objects.get(name=tournament_name)
            if match not in tournament.get_current_schedule():
                messages.add_message(request, messages.WARNING, "This match is not part of the requested tournament")
                return redirect('show_schedule', tournament_name=tournament_name, club_name=club_name)
            else:
                return view_function(request, *args, **kwargs)

    return modified_view_function


def must_be_valid_result(view_function):
    def modified_view_function(request, *args, **kwargs):
        result = kwargs.get('result')
        club_name = kwargs.get('club_name')
        tournament_name = kwargs.get('tournament_name')
        valid_results = ['draw', 'player1', 'player2']
        if result not in valid_results:
            messages.add_message(request, messages.WARNING, "This result is not valid")
            return redirect('show_schedule', tournament_name=tournament_name, club_name=club_name)
        else:
            return view_function(request, *args, **kwargs)

    return modified_view_function


def tournament_has_not_finished(view_function):
    def modified_view_function(request, *args, **kwargs):
        club_name = kwargs.get('club_name')
        tournament_name = kwargs.get('tournament_name')
        tournament = Tournament.objects.get(name=tournament_name)
        if tournament.has_finished():
            messages.add_message(request, messages.WARNING, "The tournament is already finished!")
            return redirect('show_tournament', tournament_name=tournament_name, club_name=club_name)
        else:
            return view_function(request, *args, **kwargs)

    return modified_view_function


def tournament_has_not_started(view_function):
    def modified_view_function(request, *args, **kwargs):
        club_name = kwargs.get('club_name')
        tournament_name = kwargs.get('tournament_name')
        tournament = Tournament.objects.get(name=tournament_name)
        if tournament.has_started():
            messages.add_message(request, messages.WARNING, "The tournament has already started!")
            return redirect('show_tournament', tournament_name=tournament_name, club_name=club_name)
        else:
            return view_function(request, *args, **kwargs)

    return modified_view_function
