"""Models in the chessclubs app."""
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar


class UserManager(BaseUserManager):
    """User manager used for creation of users"""

    def create_user(self, email, first_name, last_name, bio, chess_experience, personal_statement, password=None,
                    is_admin=False, is_staff=False, is_active=True):
        """Create a user according to User model"""
        if not email:
            raise ValueError("User must have an email")
        if not password:
            raise ValueError("User must have a password")
        if not first_name:
            raise ValueError("User must have a first name")
        if not last_name:
            raise ValueError("User must have a last name")
        if not chess_experience:
            raise ValueError("User must have a chess experience")
        if not personal_statement:
            raise ValueError("User must have a personal statement")

        user = self.model(
            email=self.normalize_email(email)
        )
        user.first_name = first_name
        user.last_name = last_name
        user.bio = bio
        user.chess_experience = chess_experience
        user.personal_statement = personal_statement
        user.set_password(password)  # change password to hash
        user.admin = is_admin
        user.staff = is_staff
        user.active = is_active
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """Create a super user with email and password only"""
        if not email:
            raise ValueError("User must have an email")
        if not password:
            raise ValueError("User must have a password")

        user = self.model(
            email=self.normalize_email(email)
        )
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractUser):
    """User model used for authentication"""
    username = None  # Don't use the username field inherited from the AbstractUser Model
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False, null=False)
    bio = models.CharField(max_length=520, blank=True)
    chess_experience = models.CharField(max_length=50, blank=False)
    personal_statement = models.CharField(max_length=1500, blank=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Required fields for when creating a superuser (other than USERNAME_FIELD and password that are always required)


    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        return self.gravatar(size=60)

    objects = UserManager()

    class Meta:
        """" All permissions associated with the User Model"""
        permissions = [
            ("access_members_list", "Can access the list of members"),
            ("show_public_info", "Can access a member's public info"),
            ("show_private_info", "Can access a member's private info"),
            ("promote", "Can promote members"),
            ("demote", "Can demote officers"),
            ("transfer_ownership", "Can transfer ownership to an officer"),
            ("manage_applications", "Can manage applications")
        ]

    def status(self):
        if self.groups.filter(name="applicants").exists():
            return "applicant"
        elif self.groups.filter(name="members").exists():
            return "member"
        elif self.groups.filter(name="officers").exists():
            return "officer"
        elif self.groups.filter(name="owner").exists():
            return "owner"
        elif self.groups.filter(name="denied_applicants").exists():
            return "denied_applicants"
        elif self.groups.filter(name="owner").exists():
            return "owner"
        else:
            return "undefined"
