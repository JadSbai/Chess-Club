"""Models in the chessclubs app."""
from django.contrib import auth

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.exceptions import PermissionDenied
from django.db import models
from libgravatar import Gravatar


class UserManager(BaseUserManager):
    """Custom user manager used for creation of users and superusers"""

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
    personal_statement = models.CharField(max_length=500, blank=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Required fields for when creating a superuser (other than USERNAME_FIELD and password that are always required)

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def clubs_count(self):
        """returns the number of clubs the user is in"""
        return self.clubs.count()

    def get_all_clubs(self):
        return self.clubs.all()

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        return self.gravatar(size=60)

    def has_club_perm(self, perm, club):
        """Return True if the user has the specified permission in a club."""
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        # Otherwise we need to check the backends.
        return _user_has_club_perm(self, perm, club)

    objects = UserManager()


class Club(models.Model):
    """Model for representing a club"""
    name = models.CharField(max_length=50, blank=False, unique=True, null=False)
    location = models.CharField(max_length=50, blank=False)
    description = models.CharField(max_length=520, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name="clubs")  # All members of the club (members, officers, owner)

    owner_permissions = []

    def is_member(self, user):
        """returns whether user is a member of a certain group"""
        return user in self.members.all()

    def member_count(self):
        """returns the number is members in the club"""
        return self.members.count()

    def get_members(self):
        """returns a querySet of all members"""
        return self.members.all()

    def add_member(self, user):
        self.members.add(user)
        self.add_to_members_group(user)

    def remove_member(self, user):
        self.members.remove(user)
        self.add_to_logged_in_non_members_group(user)

    def toggle_membership(self, user):
        if self.is_member(user):
            self.remove_member(user)
        else:
            self.add_member(user)

    def __members_group(self):
        members, created = Group.objects.get_or_create(name=f"{self.name}_members")
        return members

    def applicants_group(self):
        applicants, created = Group.objects.get_or_create(name=f"{self.name}_applicants")
        return applicants

    def __denied_applicants_group(self):
        denied_applicants, created = Group.objects.get_or_create(name=f"{self.name}_denied_applicants")
        return denied_applicants

    def __officers_group(self):
        officers, created = Group.objects.get_or_create(name=f"{self.name}_officers")
        return officers

    def __authenticated_non_member_group(self):
        non_members, created = Group.objects.get_or_create(name=f"{self.name}_authenticated_non_members")
        return non_members

    def add_to_members_group(self, user):
        self.__members_group().user_set.add(user)

    def remove_from_members_group(self, user):
        self.__members_group().user_set.remove(user)

    def add_to_applicants_group(self, user):
        self.applicants_group().user_set.add(user)

    def remove_from_applicants_group(self, user):
        self.applicants_group().user_set.remove(user)

    def add_to_denied_applicants_group(self, user):
        self.__denied_applicants_group().user_set.add(user)

    def remove_from_denied_applicants_group(self, user):
        self.__denied_applicants_group().user_set.remove(user)

    def add_to_officers_group(self, user):
        self.__officers_group().user_set.add(user)

    def remove_from_officers_group(self, user):
        self.__officers_group().user_set.remove(user)

    def add_to_logged_in_non_members_group(self, user):
        self.__authenticated_non_member_group().user_set.add(user)

    def remove_from_logged_in_non_members_group(self, user):
        self.__authenticated_non_member_group().user_set.remove(user)

    def assign_owner_permissions(self):
        for permission in self.owner_permissions:
            permission.add_user(self.owner)

    def remove_owner_permissions(self):
        for permission in self.owner_permissions:
            permission.remove_user(self.owner)

    def set_owner_permissions(self, permissions):
        self.owner_permissions = permissions

    def change_owner(self, user):
        self.remove_from_officers_group(user)
        self.remove_owner_permissions()
        self.add_to_officers_group(self.owner)
        self.owner = user
        self.assign_owner_permissions()

    def user_status(self, user):
        """Returns the status of a given user in the club (assumes a user belongs to one and only one group)"""
        if user in self.__authenticated_non_member_group().user_set.all():
            return "authenticated_non_member_user"
        elif user in self.applicants_group().user_set.all():
            return "applicant"
        elif user in self.__denied_applicants_group().user_set.all():
            return "denied_applicant"
        elif user in self.__members_group().user_set.all():
            return "member"
        elif user in self.__officers_group().user_set.all():
            return "officer"
        elif user == self.owner:
            return "owner"
        else:
            return "anonymous"

    def assign_club_groups_permissions(self):
        """Create and assign club-specific permissions to the club's groups and owner"""
        # Get the base permissions
        access_club_info_perm = Permission.objects.get(codename="access_club_info")
        access_club_owner_info_perm = Permission.objects.get(codename="access_club_owner_public_info")
        members_list_perm = Permission.objects.get(codename='access_members_list')
        public_perm = Permission.objects.get(codename='show_public_info')
        private_perm = Permission.objects.get(codename='show_private_info')
        manage_applications_perm = Permission.objects.get(codename='manage_applications')
        promote_perm = Permission.objects.get(codename='promote')
        demote_perm = Permission.objects.get(codename='demote')
        transfer_ownership_perm = Permission.objects.get(codename='transfer_ownership')
        acknowledge_denial_perm = Permission.objects.get(codename='acknowledge_denial')

        # Create the club-specific permissions
        access_club_info, created = ClubPermission.objects.get_or_create(club=self,
                                                                         base_permission=access_club_info_perm)
        access_club_owner_info, created = ClubPermission.objects.get_or_create(club=self,
                                                                               base_permission=access_club_owner_info_perm)
        members_list, created = ClubPermission.objects.get_or_create(club=self, base_permission=members_list_perm)
        public, created = ClubPermission.objects.get_or_create(club=self, base_permission=public_perm)
        private, created = ClubPermission.objects.get_or_create(club=self, base_permission=private_perm)
        manage_applications, created = ClubPermission.objects.get_or_create(club=self,
                                                                            base_permission=manage_applications_perm)
        promote, created = ClubPermission.objects.get_or_create(club=self, base_permission=promote_perm)
        demote, created = ClubPermission.objects.get_or_create(club=self, base_permission=demote_perm)
        transfer_ownership, created = ClubPermission.objects.get_or_create(club=self,
                                                                           base_permission=transfer_ownership_perm)
        acknowledge_denial, created = ClubPermission.objects.get_or_create(club=self,
                                                                           base_permission=acknowledge_denial_perm)

        # Assign the appropriate groups and/or users to the the club permissions (according to the requirements)
        groups = [self.__officers_group(), self.applicants_group(), self.__denied_applicants_group(),
                  self.__authenticated_non_member_group(), self.__members_group()]
        access_club_info.set_groups(groups)
        access_club_owner_info.set_groups(groups)
        groups = [self.__denied_applicants_group()]
        acknowledge_denial.set_groups(groups)
        groups = [self.__officers_group(), self.__members_group()]
        members_list.set_groups(groups)
        public.set_groups(groups)
        groups = [self.__officers_group()]
        private.set_groups(groups)
        manage_applications.set_groups(groups)

        # Set and assign the owner's permissions
        self.set_owner_permissions(
            [access_club_info, access_club_owner_info, members_list, public, private, manage_applications, promote,
             demote, transfer_ownership])
        self.assign_owner_permissions()

    class Meta:
        """" All base permissions associated with the Club Model"""
        permissions = [
            ("access_members_list", "Can access the list of members"),
            ("show_public_info", "Can access a member's public info"),
            ("show_private_info", "Can access a member's private info"),
            ("promote", "Can promote members"),
            ("demote", "Can demote officers"),
            ("transfer_ownership", "Can transfer ownership to an officer"),
            ("manage_applications", "Can manage applications"),
            ("access_club_info", "Can access a club's public info"),
            ("access_club_owner_public_info", "Can access a club owner public info"),
            ("acknowledge_denial", "Can acknowledge denial of application"),
        ]


class ClubPermission(models.Model):
    """A permission that is valid for a specific club."""

    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    base_permission = models.ForeignKey(
        Permission, on_delete=models.CASCADE, related_name="club_permission"
    )
    users = models.ManyToManyField(User, related_name="user_club_permissions")
    groups = models.ManyToManyField(Group, related_name="club_permissions")

    def set_groups(self, groups):
        for group in groups:
            self.groups.add(group)

    def add_user(self, user):
        self.users.add(user)

    def remove_user(self, user):
        self.users.remove(user)

    class Meta:
        indexes = [models.Index(fields=["club", "base_permission"])]
        unique_together = ["club", "base_permission"]


def _user_has_club_perm(user, perm, club):
    """Checks whether a given user has the required permission in the the specified club"""
    for backend in auth.get_backends():
        if not hasattr(backend, "has_club_perm"):
            continue
        try:
            if backend.has_club_perm(user, perm, club):
                return True
        except PermissionDenied:
            return False
    return False
