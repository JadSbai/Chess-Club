"""Views of the chessclubs app."""
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render, get_object_or_404
from notifications.models import Notification
from notifications.utils import slug2id
from .forms import LogInForm, PasswordForm, UserForm, SignUpForm, ClubForm
from .decorators import login_prohibited, club_permission_required
from .models import User, Club
from notifications.signals import notify


@login_required
def my_profile(request):
    current_user = request.user
    return render(request, 'my_profile.html', {'user': current_user})


@login_prohibited
def log_in(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)
        next = request.POST.get('next') or ''
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                redirect_url = next or 'my_profile'
                return redirect(redirect_url)
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
    else:
        next = request.GET.get('next') or ''
    form = LogInForm()
    return render(request, 'log_in.html', {'form': form, 'next': next})


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
            return redirect('my_profile')
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})


@login_required
@club_permission_required('chessclubs.show_public_info')
def show_user(request, user_id, club_name):
    try:
        target_user = User.objects.get(id=user_id)
        club = Club.objects.get(name=club_name)
    except ObjectDoesNotExist:
        return redirect('user_list', club_name=club_name)
    else:
        current_user_status = club.user_status(request.user)
        target_user_status = club.user_status(target_user)
        return render(request, 'show_user.html',
                      {'target_user': target_user, 'club': club, 'current_user_status': current_user_status,
                       'target_user_status': target_user_status})


@login_required
@club_permission_required('chessclubs.access_members_list')
def user_list(request, club_name):
    try:
        club = Club.objects.get(name=club_name)
    except ObjectDoesNotExist:
        return redirect('clubs_list')
    else:
        users = club.get_members()
        current_user = request.user
        return render(request, 'user_list.html', {'users': users, 'current_user': current_user, 'club': club})


@login_required
@club_permission_required('chessclubs.promote')
def promote(request, user_id, club_name):
    try:
        target_user = User.objects.get(id=user_id)
        club = Club.objects.get(name=club_name)
    except ObjectDoesNotExist:
        return redirect('view_applications', club_name=club_name)
    else:
        club.remove_from_members_group(target_user)
        club.add_to_officers_group(target_user)
        notify.send(request.user, recipient=target_user, verb='Message',
                    description=f"You have been promoted to Officer of club {club_name}")
        return redirect('show_user', club_name=club_name, user_id=user_id)


@login_required
@club_permission_required('chessclubs.demote')
def demote(request, user_id, club_name):
    try:
        target_user = User.objects.get(id=user_id)
        club = Club.objects.get(name=club_name)
    except ObjectDoesNotExist:
        return redirect('view_applications', club_name=club_name)
    else:
        club.remove_from_officers_group(target_user)
        club.add_to_members_group(target_user)
        notify.send(request.user, recipient=target_user, verb='Message',
                    description=f"You have been demoted to Member of club {club.name}")
        return redirect('show_user', club_name=club_name, user_id=user_id)


@login_required
@club_permission_required('chessclubs.transfer_ownership')
def transfer_ownership(request, user_id, club_name):
    try:
        target_user = User.objects.get(id=user_id)
        club = Club.objects.get(name=club_name)
    except ObjectDoesNotExist:
        return redirect('view_applications', club_name=club_name)
    else:
        club.change_owner(target_user)
        notify.send(request.user, recipient=target_user, verb='Message',
                    description="You have been transfered the ownership of the club")
        return redirect('show_user', club_name=club_name, user_id=user_id)


@login_required
def mark_as_read(request, slug=None):
    notification_id = slug2id(slug)
    notification = get_object_or_404(
        Notification, recipient=request.user, id=notification_id)
    notification.mark_as_read()
    return redirect('my_profile')


@login_required
@club_permission_required('chessclubs.manage_applications')
def view_applications(request, club_name):
    try:
        club = Club.objects.get(name=club_name)
    except ObjectDoesNotExist:
        return redirect('my_profile')
    else:
        applicants = club.applicants_group().user_set.all()
        count = len(applicants)
        return render(request, 'applicants_list.html', {'applicants': applicants, 'count': count, 'club': club})


@login_required
@club_permission_required('chessclubs.manage_applications')
def accept(request, user_id, club_name):
    try:
        club = Club.objects.get(name=club_name)
        target_user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return redirect('view_applications', club_name)
    else:
        club.add_to_members_group(target_user)
        club.remove_from_applicants_group(target_user)
        notify.send(request.user, recipient=target_user, verb='Message',
                    description=f"Your application for club {club_name} has been accepted")
        return redirect('view_applications', club_name)


@login_required
@club_permission_required('chessclubs.manage_applications')
def deny(request, user_id, club_name):
    try:
        club = Club.objects.get(name=club_name)
        target_user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return redirect('view_applications', club_name)
    else:
        club.add_to_denied_applicants_group(target_user)
        club.remove_from_applicants_group(target_user)
        notify.send(request.user, recipient=target_user, verb='Message',
                    description=f"Your application for club {club_name} has been denied")
        return redirect('view_applications', club_name)


@login_required
@permission_required('chessclubs.acknowledge_denial')
def acknowledged(request, club_name):
    try:
        club = Club.objects.get(name=club_name)
    except ObjectDoesNotExist:
        return redirect('my_profile')
    else:
        club.add_to_logged_in_non_members_group(request.user)
        club.remove_from_denied_applicants_group(request.user)
        return redirect('my_profile')


def page_not_found_view(request, exception):
    return render(request, '404.html', status=404)


@login_required
def create_club(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            current_user = request.user
            form = ClubForm(request.POST)
            if form.is_valid():
                club = form.save(current_user)
                return redirect('my_profile')
            else:
                return render(request, 'create_club.html', {'form': form})
        else:
            return redirect('log_in')
    else:
        form = ClubForm()
        return render(request, 'create_club.html', {'form': form})


@login_required
def clubs_list(request):
    clubs = Club.objects.all()
    return render(request, 'partials/clubs_list.html', {'clubs': clubs})


@login_required
@club_permission_required(perm='chessclubs.access_club_info')
def show_club(request, club_name):
    club = Club.objects.get(name=club_name)
    return render(request, 'partials/show_club.html', {'club': club})
