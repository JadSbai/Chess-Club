"""Views of the chessclubs app."""
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render
from .forms import LogInForm, PasswordForm, UserForm, SignUpForm
from .helpers import login_prohibited
from .groups import members, officers, owner
from .models import User

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
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
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
            login(request, user)
            #members.user_set.add(user)
            #officers.user_set.add(user)
            #user.is_superuser = True
            #owner.user_set.add(user)
            #user.user_permissions.set(owner_permissions)
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
        #is_officer = request.user.status == 'officer'
        is_targert_user_officer = user.groups.filter(name='officers').exists()
        is_targert_user_member = user.groups.filter(name='members').exists()
        #is_owner = request.user.status == "owner"
        is_owner = request.user.groups.filter(name='owner').exists()

        print(is_owner)
        print(is_officer)
        print(request.user.groups.filter(name='applicants').exists())
        print(request.user.groups.filter(name='members').exists())
        #print(request.user.status)

        return render(request, 'show_user.html',
            {'user': user, 'isOfficer': is_officer, 'is_targert_user_officer': is_targert_user_officer, 'is_targert_user_member': is_targert_user_member, 'is_owner': is_owner, 'user_id':user_id }
            )

@login_required
@permission_required('chessclubs.access_members_list')
def user_list(request):
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users})


def promote(request, user_id):
    target_user = User.objects.get(id=user_id)
    target_user.groups.clear()
    officers.user_set.add(target_user)
    is_officer = target_user.groups.filter(name='officers').exists()
    print(is_officer)
    #user.groups.add(officers)
    return redirect('show_user', user_id)

def demote(request, user_id):
    target_user = User.objects.get(id=user_id)
    target_user.groups.clear()
    members.user_set.add(target_user)
    return redirect('show_user', user_id)

def transfer_ownership(request, user_id):
    target_user = User.objects.get(id=user_id)
    target_user.groups.clear()
    owner.user_set.add(target_user)
    request.user.groups.clear()
    officers.user_set.add(request.user)
    return redirect('show_user', user_id)
