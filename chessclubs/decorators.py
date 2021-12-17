from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.utils import timezone

from .models import Club, Tournament, User, Match


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
                        if perm == 'chessclubs.access_members_list':
                            messages.add_message(request, messages.WARNING,
                                                 "Permission denied! Only members of the club can access the list of members")
                            return redirect('show_club', club_name=club_name)
                        elif perm == 'chessclubs.show_public_info':
                            messages.add_message(request, messages.WARNING,
                                                 "Permission denied! Only members of the club can see a member's public info")
                            return redirect('show_club', club_name=club_name)
                        elif perm == 'chessclubs.promote' or perm == "chessclubs.demote" or perm == 'chessclubs.transfer_ownership':
                            messages.add_message(request, messages.WARNING,
                                                 "Permission denied! Only owner of the club can modify statuses of the members")
                            return redirect('show_club', club_name=club_name)
                        elif perm == 'chessclubs.manage_applications':
                            messages.add_message(request, messages.WARNING,
                                                 "Only the owner and officers can manage the club's applications")
                            return redirect('show_club', club_name=club_name)
                        elif perm == 'chessclubs.acknowledge_response':
                            messages.add_message(request, messages.WARNING,
                                                 "You can only acknowldege an application response if it has either been accepted or denied")
                            return redirect('show_club', club_name=club_name)
                        elif perm == 'chessclubs.apply_to_club':
                            messages.add_message(request, messages.WARNING,
                                                 "Only non-members can apply to a club")
                            return redirect('show_club', club_name=club_name)
                        elif perm == 'chessclubs.ban':
                            messages.add_message(request, messages.WARNING,
                                                 "Only the owner can ban a member")
                            return redirect('show_club', club_name=club_name)
                        elif perm == 'chessclubs.leave':
                            messages.add_message(request, messages.WARNING,
                                                 "Only members and officers can leave the club")
                            return redirect('show_club', club_name=club_name)
                        elif perm == 'chessclubs.create_tournament':
                            messages.add_message(request, messages.WARNING,
                                                 "Only the owner or an officer can create a tournament")
                            return redirect('show_club', club_name=club_name)
                        elif perm == 'chessclubs.join_tournament':
                            messages.add_message(request, messages.WARNING,
                                                 "Only a member of the club can join its tournaments")
                            return redirect('show_club', club_name=club_name)
                        elif perm == 'chessclubs.edit_club_info':
                            messages.add_message(request, messages.WARNING,
                                                 "Only the owner can modify the club's information")
                            return redirect('show_club', club_name=club_name)
                        elif perm == 'chessclubs.access_club_tournaments':
                            messages.add_message(request, messages.WARNING,
                                                 "You can see only see a club's tournaments if you are part of it!")
                            return redirect('show_club', club_name=club_name)
                        else:
                            messages.add_message(request, messages.WARNING,
                                                 "Permission denied! You don't have the necessary tournament permission(s)")
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


def target_user_must_be_officer_and_non_participant(view_function):
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
            tournament = Tournament.objects.get(name=tournament_name)
            club = Club.objects.get(name=club_name)
            if club.user_status(user) != "officer":
                messages.add_message(request, messages.WARNING, "You can only add officers as co-organisers")
                return redirect('show_tournament', tournament_name=tournament_name, club_name=club_name)
            elif tournament.user_status(user) != "non-participant":
                messages.add_message(request, messages.WARNING, "You can only add non-participants as co-organisers")
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


def tournament_has_started(view_function):
    def modified_view_function(request, *args, **kwargs):
        club_name = kwargs.get('club_name')
        tournament_name = kwargs.get('tournament_name')
        tournament = Tournament.objects.get(name=tournament_name)
        if not tournament.has_started():
            messages.add_message(request, messages.WARNING, "The tournament has not started yet!")
            return redirect('show_tournament', tournament_name=tournament_name, club_name=club_name)
        else:
            return view_function(request, *args, **kwargs)

    return modified_view_function
