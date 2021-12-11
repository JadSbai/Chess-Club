from notifications.signals import notify
from django.shortcuts import redirect
from chessclubs.models import User, Club, Match
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
            notify.send(user, recipient=member, verb=f'{club.name}_Leave_Notice',
                        description=f"{user.full_name()} has left club {club.name}")


def notify_officers_and_owner_of_new_application(user, club):
    for member in club.members.all():
        if club.user_status(member) == "officer" or club.user_status(member) == "owner":
            notify.send(user, recipient=member, verb=f'{club.name}_Apply',
                        description=f"{user.full_name()} has applied to club {club.name}")


def get_appropriate_redirect(notification):
    action_string = notification.verb
    action_pattern = re.search('(.*)_(.*)', action_string)
    # Not going to be kept in production
    try:
        action_name = action_pattern.group(2)
    except AttributeError:
        print("No action name")
        raise BaseException
    if action_name == "Test":
        return redirect(REDIRECT_URL_WHEN_LOGGED_IN)
    try:
        club_name = action_pattern.group(1)
    except AttributeError:
        print("No club name")
        raise BaseException

    # Not going to be kept in production
    clubs = Club.objects.all()
    valid_club_names = [club.name for club in clubs]
    if club_name not in valid_club_names:
        print("Club name is not valid")
        raise BaseException
    if action_name == "Transfer_Ownership":
        return redirect('my_profile')
    elif action_name == "Promote" or action_name == "Demote":
        return redirect('show_club', club_name=club_name)
    elif action_name == "Accept" or action_name == "Deny":
        return redirect('my_applications')
    elif action_name == "Apply":
        return redirect('view_applications', club_name=club_name)
    elif action_name == "Join":
        return redirect('user_list', club_name=club_name)
    elif action_name == "Ban":
        return redirect(REDIRECT_URL_WHEN_LOGGED_IN)
    elif action_name == "Leave":
        return redirect(REDIRECT_URL_WHEN_LOGGED_IN)
    elif action_name == "Leave_Notice":
        return redirect('user_list', club_name=club_name)
    else:
        # Not going to be kept in production
        print("Action name is not valid")
        raise BaseException





