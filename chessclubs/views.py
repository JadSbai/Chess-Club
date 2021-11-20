"""Views of the chessclubs app."""
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render, get_object_or_404
from notifications.models import Notification
from notifications.utils import slug2id

from .forms import LogInForm, PasswordForm, UserForm, SignUpForm
from .helpers import login_prohibited
from .groups import members, officers, applicants, owner
from .models import User
from notifications.signals import notify


@login_required
def my_profile(request):
    current_user = request.user
    permissions = current_user.user_permissions.all()
    return render(request, 'my_profile.html', {'user': current_user, 'permissions': permissions})


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
    print(request.user.is_superuser)
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
    """When a new user signs up, he becomes an applicant"""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            owner.user_set.add(user)
            return redirect('my_profile')
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})


@login_required
@permission_required('chessclubs.show_public_info')
def show_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return redirect('user_list')
    else:
        is_officer = request.user.groups.filter(name='officers').exists()
        is_target_user_officer = user.groups.filter(name='officers').exists()
        is_target_user_member = user.groups.filter(name='members').exists()
        is_owner = request.user.groups.filter(name='owner').exists()
        return render(request, 'show_user.html',
                      {'user': user, 'is_officer': is_officer, 'is_target_user_officer': is_target_user_officer,
                       'is_target_user_member': is_target_user_member, 'is_owner': is_owner, 'user_id': user_id}
                      )


@login_required
@permission_required('chessclubs.access_members_list')
def user_list(request):
    users = User.objects.all()
    current_user = request.user
    return render(request, 'user_list.html', {'users': users, 'current_user': current_user})


@permission_required('chessclubs.promote')
def promote(request, user_id):
    target_user = User.objects.get(id=user_id)
    target_user.groups.clear()
    officers.user_set.add(target_user)
    notify.send(request.user, recipient=target_user, verb='Message', description="You have been promoted to Officer")
    return redirect('show_user', user_id)


@permission_required('chessclubs.demote')
def demote(request, user_id):
    target_user = User.objects.get(id=user_id)
    target_user.groups.clear()
    members.user_set.add(target_user)
    notify.send(request.user, recipient=target_user, verb='Message', description="You have been demoted to Member")
    return redirect('show_user', user_id)


@permission_required('chessclubs.transfer_ownership')
def transfer_ownership(request, user_id):
    target_user = User.objects.get(id=user_id)
    target_user.groups.clear()
    owner.user_set.add(target_user)
    request.user.groups.clear()
    officers.user_set.add(request.user)
    notify.send(request.user, recipient=target_user, verb='Message', description="You have been transfered the ownership of the club")
    return redirect('show_user', user_id)

@login_required
def mark_as_read(request, slug=None):
    notification_id = slug2id(slug)
    notification = get_object_or_404(
        Notification, recipient=request.user, id=notification_id)
    notification.mark_as_read()
    return redirect('my_profile')
