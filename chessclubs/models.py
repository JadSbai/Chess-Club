"""Models in the chessclubs app."""

from django.contrib import auth
import random
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import models
from django.db.models import F
from libgravatar import Gravatar
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

TOURNAMENT_MAX_CAPACITY = 96
TOURNAMENT_MIN_CAPACITY = 2


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

    CHESS_EXPERIENCE_CHOICES = [
        ('Novice', 'Novice'),
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
        ('Expert', 'Expert'),
    ]

    username = None  # Don't use the username field inherited from the AbstractUser Model
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False, null=False)
    bio = models.CharField(max_length=520, blank=True)
    chess_experience = models.CharField(max_length=50, choices=CHESS_EXPERIENCE_CHOICES, default='novice', blank=False)
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

    def has_tournament_perm(self, perm, tournament):
        """Return True if the user has the specified permission in a tournament."""
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        # Otherwise we need to check the backends.
        return _user_has_tournament_perm(self, perm, tournament)

    def save(self, *args, **kwargs):
        self.backend = 'django.contrib.auth.backends.ModelBackend'
        super(User, self).save(*args, **kwargs)

    objects = UserManager()


class Club(models.Model):
    """Model for representing a club"""
    name = models.CharField(max_length=50, blank=False, unique=True, null=False)
    location = models.CharField(max_length=50, blank=False)
    description = models.CharField(max_length=520, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name="clubs")  # All members of the club (members, officers, owner)

    def get_seeder_groups(self):
        groups = ["officer", "applicant", "member", "logged_in_non_member"]
        return groups

    def is_member(self, user):
        """returns whether user is a member of a certain group"""
        return user in self.members.all()

    def get_club_owner(self):
        return self.owner

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

    def __accepted_applicants_group(self):
        accepted_applicants, created = Group.objects.get_or_create(name=f"{self.name}_accepted_applicants")
        return accepted_applicants

    def __owner_group(self):
        owners, created = Group.objects.get_or_create(name=f"{self.name}_owner")
        return owners

    def add_to_members_group(self, user):
        self.__members_group().user_set.add(user)

    def remove_from_members_group(self, user):
        self.__members_group().user_set.remove(user)

    def add_to_accepted_applicants_group(self, user):
        self.__accepted_applicants_group().user_set.add(user)

    def remove_from_accepted_applicants_group(self, user):
        self.__accepted_applicants_group().user_set.remove(user)

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

    def owner_count(self):
        return self.__owner_group().user_set.all().count()

    def officer_count(self):
        return self.__officers_group().user_set.all().count()

    def change_owner(self, user):
        self.remove_from_officers_group(user)
        self.__owner_group().user_set.remove(self.owner)
        self.__owner_group().user_set.add(user)
        self.add_to_officers_group(self.owner)

    def user_status(self, user):
        """Returns the status of a given user in the club (assumes a user belongs to one and only one group of each club)"""
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
        elif user in self.__accepted_applicants_group().user_set.all():
            return "accepted_applicant"
        elif user in self.__owner_group().user_set.all():
            return "owner"
        else:
            return "anonymous"

    def assign_club_groups_permissions(self):
        """Create and assign club-specific permissions to the club's groups and owner"""
        # Get the base permissions from the Club model Meta class
        access_club_info_perm = Permission.objects.get(codename="access_club_info")
        access_club_owner_info_perm = Permission.objects.get(codename="access_club_owner_public_info")
        members_list_perm = Permission.objects.get(codename='access_members_list')
        public_perm = Permission.objects.get(codename='show_public_info')
        private_perm = Permission.objects.get(codename='show_private_info')
        manage_applications_perm = Permission.objects.get(codename='manage_applications')
        promote_perm = Permission.objects.get(codename='promote')
        demote_perm = Permission.objects.get(codename='demote')
        transfer_ownership_perm = Permission.objects.get(codename='transfer_ownership')
        acknowledge_response_perm = Permission.objects.get(codename='acknowledge_response')
        apply_to_club_perm = Permission.objects.get(codename='apply_to_club')
        ban_perm = Permission.objects.get(codename='ban')
        leave_perm = Permission.objects.get(codename='leave')
        tournament_perm = Permission.objects.get(codename='create_tournament')

        # Create the club-specific permissions using the ClubPermission Model
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
        acknowledge_response, created = ClubPermission.objects.get_or_create(club=self,
                                                                             base_permission=acknowledge_response_perm)

        apply_to_club, created = ClubPermission.objects.get_or_create(club=self,
                                                                      base_permission=apply_to_club_perm)
        ban, created = ClubPermission.objects.get_or_create(club=self,
                                                            base_permission=ban_perm)
        leave, created = ClubPermission.objects.get_or_create(club=self,
                                                              base_permission=leave_perm)
        create_tournament, created = ClubPermission.objects.get_or_create(club=self,
                                                                          base_permission=tournament_perm)

        # Assign the appropriate groups to the the club-specific permissions (according to requirements)
        groups = [self.__officers_group(), self.applicants_group(), self.__denied_applicants_group(),
                  self.__authenticated_non_member_group(), self.__members_group(), self.__accepted_applicants_group(),
                  self.__owner_group()]
        access_club_info.set_groups(groups)
        access_club_owner_info.set_groups(groups)
        groups = [self.__authenticated_non_member_group()]
        apply_to_club.set_groups(groups)
        groups = [self.__denied_applicants_group(), self.__accepted_applicants_group()]
        acknowledge_response.set_groups(groups)
        groups = [self.__officers_group(), self.__members_group(), self.__owner_group()]
        members_list.set_groups(groups)
        public.set_groups(groups)
        groups = [self.__officers_group(), self.__owner_group()]
        private.set_groups(groups)
        manage_applications.set_groups(groups)
        create_tournament.set_groups(groups)
        groups = [self.__officers_group(), self.__members_group()]
        leave.set_groups(groups)
        groups = [self.__owner_group()]
        promote.set_groups(groups)
        demote.set_groups(groups)
        transfer_ownership.set_groups(groups)
        ban.set_groups(groups)
        self.__owner_group().user_set.add(self.owner)

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
            ("acknowledge_response", "Can acknowledge response (acceptance or denial) to an application"),
            ("apply_to_club", "Can apply to club"),
            ("ban", "Can ban a user from the club"),
            ("leave", "Can leave a club"),
            ("create_tournament", "Can create a tournament")
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


def validate_tournament_deadline(value):
    """Validator function for a tournament deadline"""
    if value > timezone.now():  # Deadline must be after creation date
        return value
    else:
        raise ValidationError("The deadline must be after the date and time of creation of the tournament")


class Tournament(models.Model):
    """Model for representing  a club tournament"""
    _PHASE_CHOICES = [
        ('Elimination-Rounds', 'Elimination-Rounds'),
        ('Small-Pool-Phase', 'Small-Pool-Phase'),
        ('Large-Pool-Phase', 'Large-Pool-Phase'),
    ]
    name = models.CharField(max_length=50, blank=False, unique=True)
    location = models.CharField(max_length=50, blank=False)
    max_capacity = models.IntegerField(default=2, validators=[
        MaxValueValidator(TOURNAMENT_MAX_CAPACITY, "The max capacity needs to be less than 96."),
        MinValueValidator(TOURNAMENT_MIN_CAPACITY, "The max capacity needs to be at least 2.")])
    deadline = models.DateTimeField(blank=False, validators=[validate_tournament_deadline])
    organiser = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organised_tournaments")
    co_organisers = models.ManyToManyField(User, related_name="co_organised_tournaments")
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="all_tournaments")
    _current_phase = models.CharField(max_length=50, choices=_PHASE_CHOICES, default="Elimination-Rounds", blank=False)
    _winner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="won_tournaments", default=None,
                                blank=True)
    _started = models.BooleanField(default=False)
    _finished = models.BooleanField(default=False)

    def add_participant(self, member):
        if member in self.__participants_group().user_set.all():
            print("You have already joined this tournament")
        elif member == self.organiser:
            print("The organiser cannot join the ")
        elif timezone.now() < self.deadline:
            new_player = Player.objects.create(user=member, tournament=self)
            self.players.add(new_player)
            self.add_to_participants_group(member)
            return new_player
        else:
            self._started = True
            print("The tournament has already started")

    def start_tournament(self):
        if timezone.now() >= self.deadline:
            self._started = True
            schedule = self.launch()
            self.save()
            return schedule
        else:
            print("The deadline is not yet passed")

    def launch(self):
        if 2 <= self.players.count() <= 16:
            self._current_phase = "Elimination-Rounds"
            self.elimination_round = EliminationRounds.objects.get_or_create(_tournament=self)
            self.elimination_round.add_players(self.players)
            schedule = self.elimination_round.generate_schedule()
        elif 16 < self.players.count() <= 32:
            self._current_phase = "Small-Pool-Phase"
            self.small_pool_phase, created = SmallPoolPhase.objects.get_or_create(tournament=self)
            self.small_pool_phase.add_players(self.players.all())
            schedule = self.small_pool_phase.generate_schedule()
        else:
            self._current_phase = "Large-Pool-Phase"
            schedule = None

        return schedule

    def has_started(self):
        return self._started

    def _set_current_phase(self, phase):
        self._current_phase = phase
        self.save()

    def announce_winner(self, winner):
        self._winner = winner.user
        self._finished = True
        self.save()
        # Close the tournament so no more actions are allowed

    def participants_list(self):
        return self.players.all()

    def is_max_capacity_reached(self):
        return self.players.count() == self.max_capacity

    def is_min_capacity_attained(self):
        return self.players.count() == TOURNAMENT_MIN_CAPACITY

    def co_organisers_list(self):
        return self.co_organisers.all()

    def __participants_group(self):
        participants_group, created = Group.objects.get_or_create(name=f"{self.name}_participants")
        return participants_group

    def __organisers_group(self):
        participants_group, created = Group.objects.get_or_create(name=f"{self.name}_organisers")
        return participants_group

    def add_to_participants_group(self, user):
        self.__participants_group().user_set.add(user)

    def add_to_organisers_group(self, user):
        self.__organisers_group().user_set.add(user)

    def remove_from_participants_group(self, user):
        self.__participants_group().user_set.remove(user)

    def remove_from_organisers_group(self, user):
        self.__organisers_group().user_set.remove(user)

    def assign_tournament_permissions_and_groups(self):
        # Get the base permissions from the Tournament model Meta class
        play_matches_perm = Permission.objects.get(codename="play_matches")
        enter_match_results_perm = Permission.objects.get(codename="enter_match_results")
        see_tournament_private_info_perm = Permission.objects.get(codename="see_tournament_private_info")

        # Create the club-specific permissions using the TournamentPermission Model
        play_matches, created = TournamentPermission.objects.get_or_create(tournament=self,
                                                                           base_permission=play_matches_perm)
        enter_match_results, created = TournamentPermission.objects.get_or_create(tournament=self,
                                                                                  base_permission=enter_match_results_perm)
        see_tournament_private_info, created = TournamentPermission.objects.get_or_create(tournament=self,
                                                                                          base_permission=see_tournament_private_info_perm)

        # Assign the appropriate groups to the the tournament-specific permissions (according to requirements)
        groups = [self.__participants_group()]
        play_matches.set_groups(groups)
        groups = [self.__participants_group(), self.__organisers_group()]
        see_tournament_private_info.set_groups(groups)
        org_group = self.__organisers_group()
        org_group.user_set.add(self.organiser)
        groups = [self.__organisers_group()]
        enter_match_results.set_groups(groups)

    class Meta:
        """Set of base permissions associated with tournaments"""
        permissions = [
            ("play_matches", "Can play matches"),
            ("enter_match_results", "Can enter match results"),
            ("see_tournament_private_info", "Can see tournament private info"),
        ]


class TournamentPermission(models.Model):
    """A permission that is valid for a specific tournament."""

    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    base_permission = models.ForeignKey(
        Permission, on_delete=models.CASCADE, related_name="tournament_permission"
    )
    users = models.ManyToManyField(User, related_name="user_tournament_permissions")
    groups = models.ManyToManyField(Group, related_name="tournament_permissions")

    def set_groups(self, groups):
        for group in groups:
            self.groups.add(group)

    def add_user(self, user):
        self.users.add(user)

    def remove_user(self, user):
        self.users.remove(user)

    class Meta:
        indexes = [models.Index(fields=["tournament", "base_permission"])]
        unique_together = ["tournament", "base_permission"]


def _user_has_tournament_perm(user, perm, tournament):
    """Checks whether a given user has the required permission in the the specified tournament"""
    for backend in auth.get_backends():
        if not hasattr(backend, "has_tournament_perm"):
            continue
        try:
            if backend.has_tournament_perm(user, perm, tournament):
                return True
        except PermissionDenied:
            return False
    return False


class Player(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="player_profiles")
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="players")
    _points = models.FloatField(validators=[MinValueValidator(float(0.0))], default=float(0.0))

    def get_points(self):
        return self._points

    def win(self):
        self._points += float(1.0)
        self.save()

    def draw(self):
        self._points += float(0.5)
        self.save()

    class Meta:
        indexes = [models.Index(fields=["user", "tournament"])]
        unique_together = ["user", "tournament"]
        ordering = ['-_points']


class EliminationRounds(models.Model):
    """Model for Elimination rounds of the tournament"""
    _PHASE_CHOICES = [
        ('Final', 'Final'),
        ('Semi-Final', 'Semi-Final'),
        ('Quarter-Final', 'Quarter_Final'),
        ('Eighth-Final', 'Eighth-Final'),
    ]
    _tournament = models.OneToOneField(Tournament, on_delete=models.CASCADE, related_name="elimination_round")
    _players = models.ManyToManyField(Player, related_name="elimination_rounds")
    phase = models.CharField(max_length=50, choices=_PHASE_CHOICES, default="Eighth-Final", blank=False)
    _open = models.BooleanField(default=True)
    _winner = models.ForeignKey(Player, on_delete=models.CASCADE, null=True, related_name="won_elimination_rounds",
                                default=None,
                                blank=True)

    def set_phase(self):
        if 16 >= self._players.count() >= 9:
            self.phase = "Eighth-Final"
        elif 8 >= self._players.count() >= 5:
            self.phase = "Quarter-Final"
        elif 4 >= self._players.count() >= 3:
            self.phase = "Semi-Final"
        else:
            self.phase = "Final"
        self.save()

    def add_players(self, new_players):
        for player in new_players:
            self._players.add(player)

    def remove_player(self, player):
        self._players.remove(player)

    def remove_all_players(self):
        self._players.all().delete()

    def enter_winner(self, player, match):
        winner = match.enter_winner(player)
        if self.phase == "Final" and winner:
            self._winner = winner
            self._open = False
            self.save()
            self._tournament.announce_winner(winner)
        else:
            print("Invalid entry")

    def number_of_players(self):
        return self._players.count()

    def get_players(self):
        return self._players.all()

    def clean_schedule(self):
        self.schedule.all().delete()

    def generate_schedule(self):
        if self.phase == "Final":
            self.generate_matches(1)
        elif self.phase == "Semi-Final":
            if self._players.count() == 3:
                self.generate_matches(1)
            else:
                self.generate_matches(2)
        elif self.phase == "Quarter-Final":
            count = self._players.count()
            if count == 5:
                self.generate_matches(2)
            elif count == 6 or count == 7:
                self.generate_matches(3)
            elif count == 8:
                self.generate_matches(4)
        else:
            count = self._players.count()
            if count == 9:
                self.generate_matches(4)
            elif count == 10 or count == 11:
                self.generate_matches(5)
            elif count == 12 or count == 13:
                self.generate_matches(6)
            elif count == 14 or count == 15:
                self.generate_matches(7)
            else:
                self.generate_matches(8)

        return self.schedule.all()

    def generate_matches(self, num):
        i = 0
        counter = 0
        while counter < num:
            new_match = EliminationMatch.objects.create_elimination_match(player1=self._players.all()[i],
                                                                          player2=self._players.all()[i + 1],
                                                                          tournament=self._tournament,
                                                                          elimination_round=self)
            self.schedule.add(new_match)
            i += 2
            counter += 1


class SmallPoolPhase(models.Model):
    tournament = models.OneToOneField(Tournament, on_delete=models.CASCADE, related_name="small_pool_phase")
    _qualified_players = models.ManyToManyField(Player, related_name="won_SPPhases")
    _players = models.ManyToManyField(Player, related_name="my_SPPhases")

    def add_players(self, players):
        for player in players:
            self._players.add(player)

    def add_qualified_players(self, qualified_players):
        for player in qualified_players:
            self._qualified_players.add(player)
        self.save()

    def get_players(self):
        return self._players.all()

    def get_players_count(self):
        return self._players.count()

    def get_pool_of_player(self, player):
        for pool in self.pools_schedule.all():
            if pool in player.my_small_pools.all():
                return pool

    def __create_small_pools(self, groups_of_3, groups_of_4):

        not_yet_selected_players = {0}
        not_yet_selected_players.remove(0)
        not_yet_selected_players.update(self._players.all())

        for i in range(groups_of_4):
            new_pool = SmallPool.objects.create(_small_pool_phase=self)
            pool_players = random.sample(not_yet_selected_players, 4)
            for player in pool_players:
                not_yet_selected_players.remove(player)
            new_pool.add_players(pool_players)

        for i in range(groups_of_3):
            new_pool = SmallPool.objects.create(_small_pool_phase=self)
            pool_players = random.sample(not_yet_selected_players, 3)
            for player in pool_players:
                not_yet_selected_players.remove(player)
            new_pool.add_players(pool_players)

    def generate_schedule(self):
        number_of_players = self._players.count()
        remainder = number_of_players % 4
        groups_of_4 = 0
        groups_of_3 = 0
        if remainder == 0:
            groups_of_4 = number_of_players / 4
        elif remainder == 1:
            groups_of_3 = 3
            groups_of_4 = (number_of_players - 9) / 4
        elif remainder == 2:
            groups_of_3 = 2
            groups_of_4 = (number_of_players - 6) / 4
        else:
            groups_of_3 = 1
            groups_of_4 = (number_of_players - 3) // 4

        if self.pools_schedule.count() != groups_of_4 + groups_of_3:
            self.__create_small_pools(groups_of_3, groups_of_4)
            self.__assign_matches_to_pools()
        return self.pools_schedule.all()


class SmallPool(models.Model):
    _players = models.ManyToManyField(Player, related_name="my_small_pools")
    _small_pool_phase = models.ForeignKey(SmallPoolPhase, on_delete=models.CASCADE, related_name="pools_schedule")
    _all_matches_played = models.BooleanField(default=False)

    def add_players(self, players):
        for player in players:
            if player not in self._small_pool_phase.get_players():
                raise ValidationError("One of the players is not part of the tournament")
        for player in players:
            if player not in self._players.all():
                self._players.add(player)
        self.save()

    def create_matches(self):
        for i in range(self._players.count()):
            for j in range(i + 1, self._players.count()):
                player1 = self._players.all()[i]
                player2 = self._players.all()[j]
                new_match = SmallPoolMatch.objects.create_small_pool_match(player1=player1, player2=player2,
                                                                           tournament=self._small_pool_phase.tournament,
                                                                           pool=self)
                self.small_pool_matches.add(new_match)
                self.save()

    def enter_result(self, match, result, winner=None):
        match.enter_result(result, winner)
        self._are_all_matches_played()
        if self.all_matches_played:
            self.__set_qualified_players()

    def _are_all_matches_played(self):
        self.all_matches_played = all(not m.is_open() for m in self.small_pool_matches.all())
        self.save()

    def __set_qualified_players(self):
        qualified_players = self.__get_qualified_players()
        self._small_pool_phase.add_qualified_players(qualified_players)

    def __get_qualified_players(self):
        return [self._players.all()[0], self._players.all()[1]]


class MatchManager(models.Manager):
    """Custom user manager used for creation of users and superusers"""

    def create_match(self, tournament, player1, player2):
        """Create a match according to User model"""
        if not tournament:
            raise ValueError("Match must be part of a tournament")
        if not player2:
            raise ValueError("Match must have a player2")
        if not player1:
            raise ValueError("Match must have a player1")
        if player2 == player1:
            raise ValueError("Players of a match must be distinct")
        if player1 == tournament.organiser or player2 == tournament.organiser:
            raise ValueError("The organiser cannot play matches")

        match = self.model()
        match._player1 = player1
        match._player2 = player2
        match.tournament = tournament
        return match


class Match(models.Model):
    _player1 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="matches")
    _player2 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="my_matches")
    _winner = models.ForeignKey(Player, on_delete=models.CASCADE, null=True, related_name="won_matches", default=None,
                                blank=True)
    _open = models.BooleanField(default=True)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="tournament_matches")

    objects = MatchManager()

    def enter_winner(self, player):
        if not self._open:
            raise ValidationError("This match is closed")
        if player == self._player1 or player == self._player2:
            self._winner = player
            self.__close_match()
            self.save()
            return self._winner
        else:
            raise ValueError("This player is not a player of this match")

    def enter_draw(self):
        if not self._open:
            raise ValidationError("This match is closed")
        else:
            self.__close_match()
            self.save()

    def __close_match(self):
        self._open = False

    def get_winner(self):
        return self._winner

    def is_open(self):
        return self._open

    def return_winner(self):
        if not self._open and self._winner is not None:
            return self._winner.user.full_name()
        else:
            raise ValidationError("Match still open or winner not yet determined")


class EliminationMatchManager(MatchManager):

    def create_elimination_match(self, tournament, player1, player2, elimination_round):
        match = super().create_match(tournament, player1, player2)
        match.elimination_round = elimination_round
        match.save(using=self._db)
        return match


class EliminationMatch(Match):
    elimination_round = models.ForeignKey(EliminationRounds, on_delete=models.CASCADE, related_name="schedule")

    def enter_winner(self, player):
        winner = super(EliminationMatch, self).enter_winner(player)
        if winner is not None:
            self.elimination_round.remove_player(player)
        return winner

    objects = EliminationMatchManager()


class SmallPoolMatchManager(MatchManager):

    def create_small_pool_match(self, tournament, player1, player2, pool):
        match = super().create_match(tournament, player1, player2)
        match.small_pool = pool
        match.save(using=self._db)
        return match


class SmallPoolMatch(Match):
    small_pool = models.ForeignKey(SmallPool, on_delete=models.CASCADE, related_name="small_pool_matches")

    def enter_result(self, result, winner=None):
        if result:
            self.__enter_winner(winner)
        else:
            self.__enter_draw_result()

    def __enter_winner(self, winner):
        true_winner = super(SmallPoolMatch, self).enter_winner(winner)
        self.__set_win_points(true_winner)

    def __enter_draw_result(self):
        super(SmallPoolMatch, self).enter_draw()
        self.__set_draw_points()

    def __set_draw_points(self):
        self._player1.draw()
        self._player2.draw()
        self.save()

    def __set_win_points(self, player):
        if player == self._player1:
            self._player1.win()
        else:
            self._player2.win()
        self.save()

    objects = SmallPoolMatchManager()
