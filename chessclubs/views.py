"""Views of the chessclubs app."""
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render, get_object_or_404
from notifications.models import Notification
from notifications.utils import slug2id
from django.urls import reverse
from .forms import LogInForm, PasswordForm, UserForm, SignUpForm, ClubForm, NewOwnerForm, TournamentForm, EditClubInformationForm
from .models import User, Club, Tournament, ClubPermission, Match
from .decorators import login_prohibited, club_permissions_required, tournament_permissions_required, must_be_non_participant
from .helpers import add_all_users_to_logged_in_group, notify_officers_and_owner_of_joining, notify_officers_and_owner_of_new_application, get_appropriate_redirect, notify_officers_and_owner_of_leave
from notifications.signals import notify
from Wildebeest.settings import REDIRECT_URL_WHEN_LOGGED_IN
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone



@login_required
def my_profile(request):
    current_user = request.user
    return render(request, 'my_profile.html', {'user': current_user})


@login_prohibited
def log_in(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)
        next_url = request.POST.get('next') or ''
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                redirect_url = next_url or REDIRECT_URL_WHEN_LOGGED_IN
                return redirect(redirect_url)
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
    else:
        next_url = request.GET.get('next') or ''
    form = LogInForm()
    return render(request, 'log_in.html', {'form': form, 'next': next_url})


def log_out(request):
    logout(request)
    return redirect('home')


@login_prohibited
def home(request):
    return render(request, 'home.html')


@login_required
def password(request):
    current_user = request.user
    if request.method == 'POST':
        form = PasswordForm(data=request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            if check_password(password, current_user.password):
                new_password = form.cleaned_data.get('new_password')
                current_user.set_password(new_password)
                current_user.save()
                login(request, current_user)
                messages.add_message(request, messages.SUCCESS, "Password updated!")
                return redirect('my_profile')
    form = PasswordForm()
    return render(request, 'password.html', {'form': form})


@login_required
def change_profile(request):
    current_user = request.user
    if request.method == 'POST':
        form = UserForm(instance=current_user, data=request.POST)
        if form.is_valid():
            messages.add_message(request, messages.SUCCESS, "Profile updated!")
            form.save()
            return redirect('my_profile')
    else:
        form = UserForm(instance=current_user)
    return render(request, 'change_profile.html', {'form': form})


@login_prohibited
def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            for club in Club.objects.all():
                club.add_to_logged_in_non_members_group(user)
            login(request, user)
            return redirect(REDIRECT_URL_WHEN_LOGGED_IN)
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})


@login_required
@club_permissions_required(perms_list=['chessclubs.show_public_info'])
def show_user(request, user_id, club_name):
    try:
        target_user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, "The user you are looking for does not exist!")
        return redirect('user_list', club_name=club_name)
    else:
        club = Club.objects.get(name=club_name)
        current_user_status = club.user_status(request.user)
        target_user_status = club.user_status(target_user)
        return render(request, 'show_user.html',
                      {'target_user': target_user, 'club': club, 'current_user_status': current_user_status,
                       'target_user_status': target_user_status})


@login_required
@club_permissions_required(perms_list=['chessclubs.access_members_list'])
def user_list(request, club_name):
    club = Club.objects.get(name=club_name)
    users = club.get_members()
    current_user = request.user
    return render(request, 'user_list.html', {'users': users, 'current_user': current_user, 'club': club})


@login_required
@club_permissions_required(perms_list=['chessclubs.promote'])
def promote(request, user_id, club_name):
    try:
        target_user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, "The user you are looking for does not exist!")
        return redirect('user_list', club_name=club_name)
    else:
        club = Club.objects.get(name=club_name)
        if target_user == request.user:
            messages.add_message(request, messages.WARNING,
                                 "You cannot promote yourself")
            return redirect('show_user', club_name=club_name, user_id=user_id)
        elif club.user_status(target_user) != "member":
            messages.add_message(request, messages.WARNING, "Only members can be promoted")
        else:
            club.remove_from_members_group(target_user)
            club.add_to_officers_group(target_user)
            notify.send(request.user, recipient=target_user, verb=f'{club.name}_Promote',
                        description=f"You have been promoted to Officer of club {club_name}")
        return redirect('show_user', club_name=club_name, user_id=user_id)


@login_required
@club_permissions_required(perms_list=['chessclubs.demote'])
def demote(request, user_id, club_name):
    try:
        target_user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, "The user you are looking for does not exist!")
        return redirect('user_list', club_name=club_name)
    else:
        club = Club.objects.get(name=club_name)
        if target_user == request.user:
            messages.add_message(request, messages.WARNING,
                                 "You cannot demote yourself")
            return redirect('show_user', club_name=club_name, user_id=user_id)
        elif club.user_status(target_user) != "officer":
            messages.add_message(request, messages.WARNING, "Only officers can be demoted")
            return redirect('show_user', club_name=club_name, user_id=user_id)
        else:
            club.remove_from_officers_group(target_user)
            club.add_to_members_group(target_user)
            notify.send(request.user, recipient=target_user, verb=f'{club.name}_Demote',
                        description=f"You have been demoted to Member of club {club.name}")
            return redirect('show_user', club_name=club_name, user_id=user_id)


@login_required
@club_permissions_required(perms_list=['chessclubs.transfer_ownership'])
def transfer_ownership(request, user_id, club_name):
    try:
        target_user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, "The user you are looking for does not exist!")
        return redirect('user_list', club_name=club_name)
    else:
        club = Club.objects.get(name=club_name)
        if target_user == request.user:
            messages.add_message(request, messages.WARNING,
                                 "You cannot transfer ownership to yourself")
            return redirect('show_user', club_name=club_name, user_id=user_id)
        elif club.user_status(target_user) != "officer":
            messages.add_message(request, messages.WARNING, "Only officers can be transferred ownership")
        else:
            club.change_owner(target_user)
            form = NewOwnerForm(instance=club, data={'owner': target_user})
            if form.is_valid():
                form.save()
            notify.send(request.user, recipient=target_user, verb=f'{club.name}_Transfer_Ownership',
                        description=f"You have been transferred the ownership of the club {club.name}")
        return redirect('show_user', club_name=club_name, user_id=user_id)


@login_required
def mark_as_read(request, slug=None):
    notification_id = slug2id(slug)
    notification = get_object_or_404(
        Notification, recipient=request.user, id=notification_id)
    notification.mark_as_read()
    return get_appropriate_redirect(notification)


@login_required
@club_permissions_required(perms_list=['chessclubs.manage_applications'])
def view_applications(request, club_name):
    club = Club.objects.get(name=club_name)
    applicants = club.applicants_group().user_set.all()
    count = len(applicants)
    return render(request, 'applicants_list.html', {'applicants': applicants, 'count': count, 'club': club})


@login_required
@club_permissions_required(perms_list=['chessclubs.manage_applications'])
def accept(request, user_id, club_name):
    try:
        target_user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, "The user you are looking for does not exist!")
        return redirect('view_applications', club_name)
    else:
        club = Club.objects.get(name=club_name)
        if target_user == request.user:
            messages.add_message(request, messages.WARNING,
                                 "You cannot accept your own application")
            return redirect('show_user', club_name=club_name, user_id=user_id)
        elif club.user_status(target_user) != "applicant":
            messages.add_message(request, messages.WARNING,
                                 "The user you want to accept is not an applicant of this club")
        else:
            club.add_to_accepted_applicants_group(target_user)
            club.remove_from_applicants_group(target_user)
            notify.send(request.user, recipient=target_user, verb=f'{club.name}_Accept',
                        description=f"Your application for club {club_name} has been accepted")
        return redirect('view_applications', club_name)


@login_required
@club_permissions_required(perms_list=['chessclubs.manage_applications'])
def deny(request, user_id, club_name):
    try:
        target_user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, "The user you are looking for does not exist!")
        return redirect('view_applications', club_name)
    else:
        club = Club.objects.get(name=club_name)
        if target_user == request.user:
            messages.add_message(request, messages.WARNING,
                                 "You cannot deny your own application")
            return redirect('show_user', club_name=club_name, user_id=user_id)
        elif club.user_status(target_user) != "applicant":
            messages.add_message(request, messages.WARNING,
                                 "The user you want to deny is not an applicant of this club")

        else:
            club.add_to_denied_applicants_group(target_user)
            club.remove_from_applicants_group(target_user)
            notify.send(request.user, recipient=target_user, verb=f'{club.name}_Deny',
                        description=f"Your application for club {club_name} has been denied")
        return redirect('view_applications', club_name)


@login_required
@club_permissions_required(perms_list=['chessclubs.acknowledge_response'])
def acknowledge(request, club_name):
    club = Club.objects.get(name=club_name)
    if club.user_status(request.user) == "accepted_applicant":
        club.add_member(request.user)
        club.remove_from_accepted_applicants_group(request.user)
        notify_officers_and_owner_of_joining(request.user, club)
        return redirect('show_club', club_name=club_name)
    elif club.user_status(request.user) == "denied_applicant":
        club.add_to_logged_in_non_members_group(request.user)
        club.remove_from_denied_applicants_group(request.user)
        return redirect('my_applications')
    else:
        messages.add_message(request, messages.WARNING,
                             "You cannot acknowledge an application that isn't yet processed or that doesn't exist")
        return redirect('my_applications')


def page_not_found_view(request, exception):
    return render(request, '404.html', status=404)


@login_required
def landing_page(request):
    current_user = request.user
    clubs = Club.objects.all()
    return render(request, 'landing_page.html', {'clubs': clubs, 'current_user': current_user})


@login_required
def create_club(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            current_user = request.user
            form = ClubForm(request.POST)
            if form.is_valid():
                club = form.save(current_user)
                add_all_users_to_logged_in_group(club)
                return redirect(REDIRECT_URL_WHEN_LOGGED_IN)
            else:
                return render(request, 'create_club.html', {'form': form})
        else:
            return redirect('log_in')
    else:
        form = ClubForm()
        return render(request, 'create_club.html', {'form': form})

@login_required
@club_permissions_required(perms_list=['chessclubs.edit_club_info'])
def edit_club(request, club_name):
    current_club = Club.objects.get(name=club_name)
    if request.method == 'POST':
        form = EditClubInformationForm(instance=current_club, data=request.POST)
        if form.is_valid():
            messages.add_message(request, messages.SUCCESS, "Club information updated!")
            form.save()
            return redirect('show_club', club_name=club_name)
        else:
            return render(request, 'edit_club_info.html', {'form': form})
    else:
        form = EditClubInformationForm(instance=current_club)
        return render(request, 'edit_club_info.html', {'form': form, 'club': current_club})

@login_required
def change_profile(request):
    current_user = request.user
    if request.method == 'POST':
        form = UserForm(instance=current_user, data=request.POST)
        if form.is_valid():
            messages.add_message(request, messages.SUCCESS, "Profile updated!")
            form.save()
            return redirect('my_profile')
    else:
        form = UserForm(instance=current_user)
    return render(request, 'change_profile.html', {'form': form})


@login_required
@club_permissions_required(perms_list=['chessclubs.access_club_info', 'chessclubs.access_club_owner_public_info'])
def show_club(request, club_name):
    club = Club.objects.get(name=club_name)
    user_status = club.user_status(request.user)
    tournaments = club.get_all_tournaments()
    return render(request, 'show_club.html',
                  {'club': club, 'user': request.user, 'user_status': user_status, 'tournaments': tournaments})


@login_required
@club_permissions_required(perms_list=['chessclubs.apply_to_club'])
def apply_club(request, club_name):
    club = Club.objects.get(name=club_name)
    target_user = request.user
    club.remove_from_logged_in_non_members_group(target_user)
    club.add_to_applicants_group(target_user)
    notify_officers_and_owner_of_new_application(request.user, club)
    return redirect('my_applications')


@login_required
def my_applications(request):
    applications = []
    denied_applications = []
    accepted_applications = []
    for club in Club.objects.all():
        if club.user_status(request.user) == "applicant":
            applications.append(club)
        elif club.user_status(request.user) == "denied_applicant":
            denied_applications.append(club)
        elif club.user_status(request.user) == "accepted_applicant":
            accepted_applications.append(club)
    count = len(applications) + len(denied_applications) + len(accepted_applications)
    return render(request, 'my_applications.html',
                  {'applications': applications, 'count': count, 'denied_applications': denied_applications,
                   'accepted_applications': accepted_applications})


@login_required
@club_permissions_required(perms_list=['chessclubs.create_tournament'])
def create_tournament(request, club_name):
    try:
        club = Club.objects.get(name=club_name)
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, "The club you are looking for does not exist!")
        return redirect(REDIRECT_URL_WHEN_LOGGED_IN)
    if request.method == 'POST':
        if request.user.is_authenticated:
            current_user = request.user
            form = TournamentForm(request.POST)
            if form.is_valid():
                tournament = form.save(current_user, club)
                club_name = club.name
                tournament_name = form.cleaned_data.get('name')
                return redirect('show_tournament', club_name=club_name, tournament_name=tournament_name)
            else:
                return render(request, 'create_tournament.html', {'form': form, 'club': club})
        else:
            return redirect('log_in')
    else:
        form = TournamentForm()
        return render(request, 'create_tournament.html', {'form': form, 'club': club})


@login_required
@club_permissions_required(perms_list=['chessclubs.ban'])
def ban(request, club_name, user_id):
    try:
        target_user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, "The user you are looking for does not exist!")
        return redirect('user_list', club_name=club_name)
    else:
        club = Club.objects.get(name=club_name)
        if target_user == request.user:
            messages.add_message(request, messages.WARNING,
                                 "You cannot ban yourself")
            return redirect('show_user', club_name=club_name, user_id=user_id)
        elif club.user_status(target_user) != "member":
            messages.add_message(request, messages.WARNING,
                                 "The user you want to ban is not a member of your club. You cannot ban officers.")
            return redirect('user_list', club_name=club_name)
        else:
            club.remove_from_members_group(target_user)
            club.remove_member(target_user)
            notify.send(request.user, recipient=target_user, verb=f'{club.name}_Ban',
                        description=f"You have been banned from {club.name}")
            return redirect('user_list', club_name=club_name)


@login_required
@club_permissions_required(perms_list=['chessclubs.leave'])
def leave(request, club_name):
    club = Club.objects.get(name=club_name)
    if club.user_status(request.user) == "officer":
        club.remove_from_officers_group(request.user)
        club.remove_member(request.user)
    elif club.user_status(request.user) == "member":
        club.remove_from_members_group(request.user)
        club.remove_member(request.user)
    notify.send(request.user, recipient=request.user, verb=f'{club.name}_Leave',
                description=f"You have left {club.name}")
    notify_officers_and_owner_of_leave(request.user, club)
    return redirect('landing_page')

@login_required
@club_permissions_required(perms_list=['chessclubs.access_club_info', 'chessclubs.access_club_owner_public_info'])
def show_tournament(request, club_name, tournament_name):
    try:
        user = request.user
        tournament = Tournament.objects.get(name=tournament_name)
        is_participant = tournament.is_participant(user)
        is_organiser = tournament.is_organiser(request.user)
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, "The tournament you are looking for does not exist!")
        return redirect('show_club', club_name=club_name)
    else:
        club = Club.objects.get(name=club_name)
        officers = club.get_officers()
        can_be_added_as_co_organiser = []
        for officer in officers:
            if officer not in tournament.participants_list() and officer not in tournament.co_organisers_list() and (
                    officer != tournament.organiser):
                can_be_added_as_co_organiser.append(officer)
        return render(request, 'show_tournament.html', {'tournament': tournament, 'user': request.user,
                                                        'allowed_co_organisers': can_be_added_as_co_organiser})


@login_required
@club_permissions_required(perms_list=['chessclubs.access_club_info', 'chessclubs.access_club_owner_public_info', 'chessclubs.apply_tournament'])
@must_be_non_participant
def apply_tournament(request, club_name, tournament_name):
    target_user = request.user
    tournament = Tournament.objects.get(name=tournament_name)
    if tournament.deadline > timezone.now():
        if not tournament.is_max_capacity_reached():
            if tournament.is_organiser(target_user):
                messages.add_message(request, messages.WARNING, "You are the organiser of this tournament. You cannot apply.")
            else:
                tournament.add_participant(target_user)
                messages.add_message(request, messages.SUCCESS, "You have successfully registered for the tournament.")

        else:
            messages.add_message(request, messages.WARNING, "Maximum capacity of participants is reached. "
                                                            "Come back next time.")
    else:
        messages.add_message(request, messages.WARNING, "You cannot apply after the deadline.")
    return redirect('show_tournament', club_name=club_name, tournament_name=tournament_name)


@login_required
@club_permissions_required(perms_list=['chessclubs.access_club_info', 'chessclubs.access_club_owner_public_info', 'chessclubs.withdraw_tournament'])
@tournament_permissions_required(perms_list=['chessclubs.withdraw'])
def withdraw_tournament(request, club_name, tournament_name):
    target_user = request.user
    tournament = Tournament.objects.get(name=tournament_name)
    if tournament.deadline > timezone.now():
        if tournament.is_participant(target_user):
            tournament.remove_participant(target_user)
        elif tournament.is_organiser(target_user):
            messages.add_message(request, messages.WARNING, "You are the organiser of this tournament. "
                                                            "You cannot apply and withdraw from your own tournaments.")
        elif not tournament.is_participant(target_user):
            messages.add_message(request, messages.WARNING, "You are not a participant of this tournament.")
    else:
        messages.add_message(request, messages.WARNING, "You cannot withdraw after the deadline.")
    return redirect('show_tournament', club_name=club_name, tournament_name=tournament_name)

@login_required
@club_permissions_required(perms_list=['chessclubs.access_club_info', 'chessclubs.access_club_owner_public_info'])
def show_schedule(request, club_name, tournament_name):
    tournament = Tournament.objects.get(name=tournament_name)
    if tournament.has_started():
        schedule = tournament.get_current_schedule()
        pools = tournament.get_current_pool_phase().pools.all()
        try:
            club = Club.objects.get(name=club_name)
        except ObjectDoesNotExist:
            messages.add_message(request, messages.ERROR, "The club you are looking for does not exist!")
            return redirect(REDIRECT_URL_WHEN_LOGGED_IN)
        return render(request, 'show_tournament_schedule.html', {'tournament': tournament, 'user': request.user, 'club': club, 'schedule':schedule, 'pools':pools})
    else:
        messages.add_message(request, messages.ERROR, "The tournament has not started yet")
        return redirect('show_tournament', tournament_name=tournament_name, club_name=club_name)

@login_required
def set_deadline_now(request, tournament_name, club_name):
    tournament = Tournament.objects.get(name=tournament_name)
    tournament.set_deadline_now()
    #tournament.start_tournament()
    print(tournament.deadline)
    return redirect('show_tournament', tournament_name=tournament_name, club_name=club_name)



@login_required
def my_matches(request):
    matches = []
    tournaments = {}
    my_tournaments = request.user.get_all_tournaments()
    for tournament in my_tournaments:
        if not tournament.has_finished():
            tournaments[tournament] = tournament.get_matches_of_player(request.user)
            matches.extend(tournament.get_matches_of_player(request.user))
    count = len(matches)
    return render(request, 'my_matches.html', {'count': count, 'tournaments': tournaments})


@login_required
def add_to_co_organiser(request, tournament_name, club_name, user_id):
    tournament = Tournament.objects.get(name=tournament_name)
    co_organiser = User.objects.get(id=user_id)
    tournament.add_co_organiser(co_organiser)
    notify.send(request.user, recipient=co_organiser, verb=f'{tournament_name}_Coorganiser',
                description=f"You have been added as co-organiser of tournament {tournament_name}")
    return redirect('show_tournament', tournament_name=tournament_name, club_name=club_name)

@club_permissions_required(perms_list=['chessclubs.access_club_info', 'chessclubs.access_club_owner_public_info'])
def enter_result(request, tournament_name, match_id, result, club_name):
    tournament = Tournament.objects.get(name=tournament_name)
    match = Match.objects.get(id=match_id)
    if result == "draw":
        if tournament.get_current_phase()!="Elimination Round":
            tournament.enter_result(match, result=False)
            if tournament.has_finished():
                return redirect('show_tournament', club_name=club_name, tournament_name=tournament_name)
            return redirect('show_schedule', club_name=club_name, tournament_name=tournament_name)
        else:
            messages.add_message(request, messages.WARNING, "You cannot enter a draw result for an elimination round")
    elif result == "player1":
        tournament.enter_result(match, winner=match.get_player1())
        if tournament.has_finished():
            return show_tournament(request, club_name=club_name, tournament_name=tournament_name)
        return show_schedule(request, club_name=club_name, tournament_name=tournament_name)
    else:
        tournament.enter_result(match, winner=match.get_player2())
        if tournament.has_finished():
            return show_tournament(request, club_name=club_name, tournament_name=tournament_name)
        return show_schedule(request, club_name=club_name, tournament_name=tournament_name)


@login_required
def publish_schedule(request, tournament_name, club_name):
    tournament = Tournament.objects.get(name=tournament_name)
    tournament.publish_schedule()
    return redirect('show_tournament', club_name=club_name, tournament_name=tournament_name)


@login_required
def start_tournament(request, tournament_name, club_name):
    tournament = Tournament.objects.get(name=tournament_name)
    if tournament.is_organiser(request.user):
        tournament.start_tournament()
    return redirect('show_tournament', tournament_name=tournament_name, club_name=club_name)
