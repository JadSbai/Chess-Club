"""Forms for the chessclubs app."""
from django import forms
from django.forms.widgets import DateInput
from django.core.validators import RegexValidator
from .models import User, Club, Tournament

class LogInForm(forms.Form):
    """Form enabling registered users to log in."""

    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())


class UserForm(forms.ModelForm):
    """Form to update user profiles."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'bio', 'chess_experience', 'personal_statement']
        widgets = {'bio': forms.Textarea(attrs={"rows": 5, "cols": 20}), 'personal_statement': forms.Textarea()}


class PasswordForm(forms.Form):
    """Form enabling users to change their password."""

    password = forms.CharField(label='Current password', widget=forms.PasswordInput())
    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
        )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')


class SignUpForm(forms.ModelForm):
    """Form enabling site visitors to sign up."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'bio', 'chess_experience', 'personal_statement']
        widgets = {
            'bio': forms.Textarea(),
            'personal_statement': forms.Textarea(),
        }

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number.'
        )],
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')

    def save(self):
        """Create a new user."""

        super().save(commit=False)
        user = User.objects.create_user(
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            bio=self.cleaned_data.get('bio'),
            password=self.cleaned_data.get('new_password'),
            chess_experience=self.cleaned_data.get('chess_experience'),
            personal_statement=self.cleaned_data.get('personal_statement')
        )
        user.backend = 'django.contrib.auth.backends.ModelBackend'  # Set the user's authentication backend
        return user


class ClubForm(forms.ModelForm):
    """Form enabling users to create clubs."""

    class Meta:
        model = Club
        fields = ['name', 'description', 'location']
        widgets = {
            'description': forms.Textarea(),
        }

    def save(self, owner):
        """Create a new club."""

        super().save(commit=False)
        club = Club.objects.create(
            name=self.cleaned_data.get('name'),
            description=self.cleaned_data.get('description'),
            location=self.cleaned_data.get('location'),
            owner=owner
        )
        club.members.add(owner)
        club.assign_club_groups_permissions()
        return club

class EditClubInformationForm(forms.ModelForm):
    """Form to update existing club information."""

    class Meta:
        model = Club
        fields = ['description', 'location']
        widgets = {'description': forms.Textarea()}

class NewOwnerForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['owner']


class TournamentForm(forms.ModelForm):
    """Form enabling users to create tournaments."""

    class Meta:
        model = Tournament
        fields = ['name', 'description', 'deadline', 'location', 'max_capacity']
        widgets = {
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(),
            'max_capacity': forms.TextInput(attrs={'min': '2', 'max': '96', 'type': 'number', 'placeholder': 'Choose a value between 2 and 96'}),
        }

    def save(self, organiser, club):
        """Create a new tournament."""

        super().save(commit=False)
        tournament = Tournament.objects.create(
            name=self.cleaned_data.get('name'),
            description=self.cleaned_data.get('description'),
            deadline=self.cleaned_data.get('deadline'),
            location=self.cleaned_data.get('location'),
            max_capacity=self.cleaned_data.get('max_capacity'),
            organiser=organiser,
            club=club
        )
        tournament.assign_tournament_permissions_and_groups()
        return tournament
