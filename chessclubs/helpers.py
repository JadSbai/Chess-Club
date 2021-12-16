from notifications.signals import notify
from django.shortcuts import redirect
from chessclubs.models import User, Club, Match, Tournament
from Wildebeest.settings import REDIRECT_URL_WHEN_LOGGED_IN
import re


def add_all_users_to_logged_in_group(club):
    for user in User.objects.all():
        if club.owner != user:
            club.add_to_logged_in_non_members_group(user)


def notify_officers_and_owner_of_joining(user, club):
    for member in club.members.all():
        if club.user_status(member) == "officer" or club.user_status(member) == "owner":
            notify.send(user, recipient=member, verb=f'{club.name}_Join',
                        description=f"{user.full_name()} has joined club {club.name}")


def notify_officers_and_owner_of_leave(user, club):
    for member in club.members.all():
        if club.user_status(member) == "officer" or club.user_status(member) == "owner":
            notify.send(user, recipient=member, verb=f'{club.name}_LeaveNotice',
                        description=f"{user.full_name()} has left club {club.name}")


def notify_participants_of_publish(tournament):
    for participant in tournament.participants_list():
        notify.send(tournament.organiser, recipient=participant.user, verb=f'{tournament.name}_PublishSchedule',
                    description=f"The schedule for tournament {tournament.name} is now published!")


def notify_participants_of_start(tournament):
    for participant in tournament.participants_list():
        notify.send(tournament.organiser, recipient=participant.user, verb=f'{tournament.name}_StartTournament',
                    description=f"The tournament {tournament.name} has started!")


def notify_officers_and_owner_of_new_application(user, club):
    for member in club.members.all():
        if club.user_status(member) == "officer" or club.user_status(member) == "owner":
            notify.send(user, recipient=member, verb=f'{club.name}_Apply',
                        description=f"{user.full_name()} has applied to club {club.name}")


def get_appropriate_redirect(notification):
    action_string = notification.verb
    action_pattern = re.search('(.*)_(.*)', action_string)
    action_name = action_pattern.group(2)
    if action_name == "Test":
        return redirect(REDIRECT_URL_WHEN_LOGGED_IN)

    instance_name = action_pattern.group(1)

    if action_name == "Promote" or action_name == "Demote" or action_name == "TransferOwnership":
        return redirect('show_club', club_name=instance_name)
    elif action_name == "Accept" or action_name == "Deny":
        return redirect('my_applications')
    elif action_name == "Apply":
        return redirect('view_applications', club_name=instance_name)
    elif action_name == "Join":
        return redirect('user_list', club_name=instance_name)
    elif action_name == "Ban" or action_name == "Leave":
        return redirect('show_club', club_name=instance_name)
    elif action_name == "LeaveNotice":
        return redirect('user_list', club_name=instance_name)
    elif action_name == "Coorganiser" or action_name == "PublishSchedule" or action_name == "StartTournament":
        tournament = Tournament.objects.get(name=instance_name)
        return redirect('show_tournament', club_name=tournament.club.name, tournament_name=instance_name)
    else:
        raise BaseException
