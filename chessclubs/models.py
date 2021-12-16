"""Models in the chessclubs app."""

from django.contrib import auth
import random
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import models, IntegrityError
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

    def get_all_tournaments(self):
        tournaments1 = []
        for player_profile in self.player_profiles.all():
            tournaments1.append(player_profile.tournament)
        return tournaments1

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

    def get_officers(self):
        return self.__officers_group().user_set.all()

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
        join_tournament_perm = Permission.objects.get(codename="join_tournament")
        edit_club_info_perm = Permission.objects.get(codename="edit_club_info")

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
        join_tournament, created = ClubPermission.objects.get_or_create(club=self,
                                                                         base_permission=join_tournament_perm)
        edit_club_info, created = ClubPermission.objects.get_or_create(club=self,
                                                                           base_permission=edit_club_info_perm)

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
        join_tournament.set_groups(groups)
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
        edit_club_info.set_groups(groups)
        self.__owner_group().user_set.add(self.owner)

    def get_all_tournaments(self):
        return self.all_tournaments.all()

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
            ("create_tournament", "Can create a tournament"),
            ("join_tournament", "Can apply to a tournament"),
            ("edit_club_info", "Can edit club information"),
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


class Player(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="player_profiles")
    tournament = models.ForeignKey('Tournament', on_delete=models.CASCADE, related_name="players")
    _points = models.FloatField(validators=[MinValueValidator(float(0.0))], default=float(0.0))
    _won_pool_phases = models.ManyToManyField('PoolPhase', related_name="PP_qualified_players")
    _elimination_round = models.ForeignKey('EliminationRounds', on_delete=models.CASCADE,
                                           related_name="EL_players", null=True, blank=True)
    _pool_phases = models.ManyToManyField('PoolPhase', related_name="PP_players")
    _pools = models.ManyToManyField('Pool', related_name="pool_players")
    _encountered_players = models.ManyToManyField('self', related_name="encountered_players")

    def get_points(self):
        return self._points

    def get_pools(self):
        return self._pools.all()

    def get_encountered_players(self):
        return self._encountered_players.all()

    def add_encountered_player(self, player):
        if player not in self.get_encountered_players():
            self._encountered_players.add(player)
            self.save()

    def _clean_encountered_players(self):
        for player in self.get_encountered_players():
            self._encountered_players.remove(player)

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


class Tournament(models.Model):
    """Model for representing  a club tournament"""
    _PHASE_CHOICES = [
        ('Elimination-Rounds', 'Elimination-Rounds'),
        ('Small-Pool-Phase', 'Small-Pool-Phase'),
        ('Large-Pool-Phase', 'Large-Pool-Phase'),
    ]

    name = models.CharField(max_length=50, blank=False, unique=True)
    description = models.CharField(max_length=240, blank=False)
    location = models.CharField(max_length=50, blank=False)
    max_capacity = models.IntegerField(default=2, validators=[
        MaxValueValidator(TOURNAMENT_MAX_CAPACITY, "The max capacity needs to be less than 96."),
        MinValueValidator(TOURNAMENT_MIN_CAPACITY, "The max capacity needs to be at least 2.")])
    deadline = models.DateTimeField(blank=False, validators=[validate_tournament_deadline])
    organiser = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organised_tournaments")
    co_organisers = models.ManyToManyField(User, related_name="co_organised_tournaments")
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="all_tournaments")
    _start_phase = models.CharField(max_length=50, choices=_PHASE_CHOICES, default="Elimination-Rounds")
    _winner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="won_tournaments", blank=True)
    _started = models.BooleanField(default=False)
    _finished = models.BooleanField(default=False)
    _schedule_published = models.BooleanField(default=False)

    def add_participant(self, member):
        new_player = Player.objects.create(user=member, tournament=self)
        self.players.add(new_player)
        self.add_to_participants_group(member)
        return new_player

    def get_participant_count(self):
        return self.players.count()

    def get_min_capacity(self):
        return TOURNAMENT_MIN_CAPACITY

    def _set_deadline_now(self):
        """Method only used for testing purposes"""
        self.deadline = timezone.now() - timezone.timedelta(days=1)
        self.save()

    def _set_deadline_future(self):
        """Method only used for testing purposes"""
        self.deadline = timezone.now() + timezone.timedelta(days=1)
        self.save()

    def is_published(self):
        return self._schedule_published

    def has_finished(self):
        return self._finished

    def _set_finished(self):
        """Method created for tests"""
        self._finished = True
        self.save()

    def enter_result(self, match, result=True, winner=None):
        pool_phase = self.get_current_pool_phase()
        if pool_phase:
            pool_match = PoolMatch.objects.get(id=match.id)
            pool_phase.enter_result(match=pool_match, result=result, winner=winner)
        else:
            elimination_match = EliminationMatch.objects.get(id=match.id)
            self.elimination_round.enter_winner(match=elimination_match, winner=winner)

    def get_winner(self):
        if self._winner:
            return self._winner.full_name()

    def get_current_phase(self):
        pool_phase = self.get_current_pool_phase()
        if pool_phase:
            return pool_phase.name
        else:
            return "Elimination Round"

    def go_to_next_phase(self, winner=None, qualified_players=None):
        if qualified_players:
            if 17 <= qualified_players.count() <= 32:
                self.__go_to_small_pool_phase(qualified_players)
                self.save()
            elif 2 <= qualified_players.count() <= 16:
                self.__go_to_elimination_round(qualified_players)
                self.save()
            else:
                raise ValidationError("Invalid number of qualified players")
        elif winner:
            self.__announce_winner(winner)
        else:
            raise ValidationError("Invalid entry")

    def __go_to_elimination_round(self, qualified_players):
        self.__create_elimination_round(qualified_players)
        self.elimination_round.generate_schedule()

    def get_current_schedule(self):
        schedule = []
        for match in self.tournament_schedule.all():
            if match.is_open():
                schedule.append(match)
        return schedule

    def get_matches_of_player(self, member):
        matches = []
        player = self.__player_instance_of_user(member)
        for match in self.get_current_schedule():
            if match.get_player1() == player or match.get_player2() == player:
                matches.append(match)
        return matches

    def __go_to_small_pool_phase(self, qualified_players):
        small_pool_phase = self.__create_pool_phase(qualified_players=qualified_players, name="Small-Pool-Phase")
        small_pool_phase.generate_schedule()

    def __create_elimination_round(self, qualified_players):
        self.elimination_round, created = EliminationRounds.objects.get_or_create(_tournament=self)
        self.elimination_round.add_players(qualified_players)
        self.elimination_round.set_phase()
        self.save()

    def __create_pool_phase(self, qualified_players, name):
        try:
            new_pool_phase = PoolPhase.objects.create(tournament=self, name=name)
        except IntegrityError:
            raise ValidationError("A pool phase with the same name already exists")
        else:
            new_pool_phase.add_players(qualified_players)
            self.pool_phases.add(new_pool_phase)
            self.save()
            return PoolPhase.objects.get(name=name, tournament=self)

    def remove_participant(self, member):
        player = self.__player_instance_of_user(member)
        player.delete()
        self.remove_from_participants_group(member)

    def _remove_all_participants(self):
        """This method is used only for tests"""
        for player in self.participants_list():
            player.delete()
            self.remove_from_participants_group(player.user)

    def get_current_pool_phase(self):
        for pool_phase in self.pool_phases.all():
            if pool_phase.is_open():
                return pool_phase
        else:
            return None

    def add_co_organiser(self, officer):
        self.co_organisers.add(officer)
        self.add_to_co_organisers_group(officer)

    def user_status(self, user):
        if user == self.organiser:
            return "organiser"
        elif user in self.co_organisers.all():
            return "co_organiser"
        elif self.__player_instance_of_user(user):
            return "participant"
        else:
            return "non-participant"

    def __set_start_phase(self):
        if 2 <= self.players.count() <= 16:
            self._start_phase = "Elimination-Rounds"
        elif 16 < self.players.count() <= 32:
            self._start_phase = "Small-Pool-Phase"
        elif 32 < self.players.count() <= 96:
            self._start_phase = "Large-Pool-Phase"
        else:
            raise ValueError("Invalid number of players")

    def remove_co_organiser(self, member):
        # Checks should be done beforehand in the views
        self.co_organisers.remove(member)
        self.remove_from_organisers_group(member)

    def start_tournament(self):
        self._started = True
        if not self._schedule_published:
            self.publish_schedule()
        self.save()

    def publish_schedule(self):
        self._schedule_published = True
        self.__set_start_phase()
        if self._start_phase == "Elimination-Rounds":
            self.__create_elimination_round(self.players.all())
            self.elimination_round.generate_schedule()
        elif self._start_phase == "Small-Pool-Phase":
            small_pool_phase = self.__create_pool_phase(qualified_players=self.players.all(), name="Small-Pool-Phase")
            small_pool_phase.generate_schedule()
        else:
            large_pool_phase = self.__create_pool_phase(qualified_players=self.players.all(), name="Large-Pool-Phase")
            large_pool_phase.generate_schedule()
        self.save()

    def has_started(self):
        return self._started

    def add_all_members_to_tournament(self):
        for member in self.club.members.all():
            self.add_participant(member)

    def __announce_winner(self, winner):
        if winner:
            self._winner = winner.user
            self._set_finished()

    def participants_list(self):
        return self.players.all()

    def is_participant(self, member):
        return self.__player_instance_of_user(member) is not None

    def __player_instance_of_user(self, member):
        for player_profile in member.player_profiles.all():
            if player_profile in self.players.all():
                return player_profile
        return None

    def is_organiser(self, member):
        return member == self.organiser

    def is_co_organiser(self, member):
        return member in self.co_organisers.all()

    def is_max_capacity_reached(self):
        return self.players.count() == self.max_capacity

    def is_min_capacity_attained(self):
        return self.players.count() == TOURNAMENT_MIN_CAPACITY

    def co_organisers_list(self):
        return self.co_organisers.all()

    def __participants_group(self):
        participants_group, created = Group.objects.get_or_create(name=f"{self.name}_participants")
        return participants_group

    def __co_organisers_group(self):
        participants_group, created = Group.objects.get_or_create(name=f"{self.name}_co_organisers")
        return participants_group

    def add_to_participants_group(self, user):
        self.__participants_group().user_set.add(user)

    def add_to_co_organisers_group(self, user):
        self.__co_organisers_group().user_set.add(user)

    def remove_from_participants_group(self, user):
        self.__participants_group().user_set.remove(user)

    def remove_from_organisers_group(self, user):
        self.__co_organisers_group().user_set.remove(user)

    def assign_tournament_permissions_and_groups(self):
        # Get the base permissions from the Tournament model Meta class
        play_matches_perm = Permission.objects.get(codename="play_matches")
        enter_match_results_perm = Permission.objects.get(codename="enter_match_results")
        see_tournament_private_info_perm = Permission.objects.get(codename="see_tournament_private_info")
        withdraw_perm = Permission.objects.get(codename="withdraw")
        add_co_organiser_perm = Permission.objects.get(codename="add_co_organiser")
        start_tournament_perm = Permission.objects.get(codename="start_tournament")
        publish_schedule_perm = Permission.objects.get(codename="publish_schedule")

        # Create the club-specific permissions using the TournamentPermission Model
        play_matches, created = TournamentPermission.objects.get_or_create(tournament=self,
                                                                           base_permission=play_matches_perm)
        enter_match_results, created = TournamentPermission.objects.get_or_create(tournament=self,
                                                                                  base_permission=enter_match_results_perm)
        see_tournament_private_info, created = TournamentPermission.objects.get_or_create(tournament=self,
                                                                                          base_permission=see_tournament_private_info_perm)
        withdraw, created = TournamentPermission.objects.get_or_create(tournament=self,
                                                                       base_permission=withdraw_perm)
        add_co_organiser, created = TournamentPermission.objects.get_or_create(tournament=self,
                                                                       base_permission=add_co_organiser_perm)
        start, created = TournamentPermission.objects.get_or_create(tournament=self,
                                                                       base_permission=start_tournament_perm)
        publish, created = TournamentPermission.objects.get_or_create(tournament=self,
                                                                               base_permission=publish_schedule_perm)

        # Assign the appropriate groups to the the tournament-specific permissions (according to requirements)
        groups = [self.__participants_group(), self.__co_organisers_group()]
        see_tournament_private_info.set_groups(groups)
        groups = [self.__participants_group()]
        play_matches.set_groups(groups)
        withdraw.set_groups(groups)
        groups = [self.__co_organisers_group()]
        enter_match_results.set_groups(groups)

        # Permissions specific to the organiser of the tournament
        enter_match_results.add_user(self.organiser)
        see_tournament_private_info.add_user(self.organiser)
        add_co_organiser.add_user(self.organiser)
        start.add_user(self.organiser)
        publish.add_user(self.organiser)

    class Meta:
        """Set of base permissions associated with tournaments"""
        permissions = [
            ("play_matches", "Can play matches"),
            ("enter_match_results", "Can enter match results"),
            ("see_tournament_private_info", "Can see tournament private info"),
            ("withdraw", "Can withdraw"),
            ("add_co_organiser", "Can add co-organiser"),
            ("start_tournament", "Can start tournament"),
            ("publish_schedule", "Can publish schedule"),
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


class EliminationRounds(models.Model):
    """Model for Elimination rounds of the tournament"""
    _PHASE_CHOICES = [
        ('Final', 'Final'),
        ('Semi-Final', 'Semi-Final'),
        ('Quarter-Final', 'Quarter_Final'),
        ('Eighth-Final', 'Eighth-Final'),
    ]
    _tournament = models.OneToOneField(Tournament, on_delete=models.CASCADE, related_name="elimination_round")
    phase = models.CharField(max_length=50, choices=_PHASE_CHOICES, default="Eighth-Final", blank=False)
    _open = models.BooleanField(default=True)
    _winner = models.OneToOneField(Player, on_delete=models.CASCADE, null=True, related_name="won_elimination_rounds",
                                   default=None,
                                   blank=True)

    def set_phase(self):
        if 16 >= self.EL_players.count() >= 9:
            self.phase = "Eighth-Final"
        elif 8 >= self.EL_players.count() >= 5:
            self.phase = "Quarter-Final"
        elif 4 >= self.EL_players.count() >= 3:
            self.phase = "Semi-Final"
        else:
            self.phase = "Final"
        self.save()

    def add_players(self, new_players):
        for player in new_players:
            self.EL_players.add(player)
        self.save()

    def __are_all_matches_played(self):
        for match in self.schedule.all():
            if match.is_open():
                return False
        return True

    def remove_player(self, player):
        self.EL_players.remove(player)
        self.save()

    def enter_winner(self, winner, match):
        # The checks will be done at views level
        if self._open:
            round_winner = match.enter_winner(winner)
            if self.phase == "Final":
                self._winner = round_winner
                self._open = False
                self.save()
                self._tournament.go_to_next_phase(winner=round_winner)
            elif self.__are_all_matches_played():
                self.__check_new_phase()
        else:
            raise ValueError("All matches have already been played")

    def __check_new_phase(self):
        before_phase = self.phase
        self.set_phase()
        if before_phase != self.phase:
            self.clean_schedule()
            self.generate_schedule()

    def number_of_players(self):
        return self.EL_players.count()

    def get_players(self):
        return self.EL_players.all()

    def get_players_count(self):
        return self.EL_players.count()

    def get_phase(self):
        return self.phase

    def clean_schedule(self):
        self.schedule.all().delete()

    def generate_schedule(self):
        if self.phase == "Final":
            self.__generate_matches(1)
        elif self.phase == "Semi-Final":
            if self.EL_players.count() == 3:
                self.__generate_matches(1)
            else:
                self.__generate_matches(2)
        elif self.phase == "Quarter-Final":
            count = self.EL_players.count()
            if count == 5:
                self.__generate_matches(2)
            elif count == 6 or count == 7:
                self.__generate_matches(3)
            elif count == 8:
                self.__generate_matches(4)
        else:
            count = self.EL_players.count()
            if count == 9:
                self.__generate_matches(4)
            elif count == 10 or count == 11:
                self.__generate_matches(5)
            elif count == 12 or count == 13:
                self.__generate_matches(6)
            elif count == 14 or count == 15:
                self.__generate_matches(7)
            else:
                self.__generate_matches(8)

        return self.schedule.all()

    def __generate_matches(self, num):
        i = 0
        counter = 0
        not_yet_selected_players = {0}
        not_yet_selected_players.remove(0)
        not_yet_selected_players.update(self.EL_players.all())

        while counter < num:
            player = random.sample(not_yet_selected_players, 1)[0]
            forbidden_players = {0}
            forbidden_players.remove(0)
            forbidden_players.update(player.get_encountered_players())
            not_yet_selected_players.remove(player)
            choices = not_yet_selected_players - forbidden_players

            if len(choices) == 0:
                random_player = random.sample(not_yet_selected_players, 1)[0]
            else:
                random_player = random.sample(choices, 1)[0]

            new_match = EliminationMatch.objects.create_elimination_match(tournament=self._tournament, player1=player,
                                                                          player2=random_player, elimination_round=self)
            not_yet_selected_players.remove(random_player)
            self.schedule.add(new_match)
            i += 1
            counter += 1


class PoolPhase(models.Model):
    _POOL_PHASE_NAME_CHOICES = [
        ('Small-Pool-Phase', 'Small-Pool-Phase'),
        ('Large-Pool-Phase', 'Large-Pool-Phase'),
    ]

    name = models.CharField(max_length=50, choices=_POOL_PHASE_NAME_CHOICES)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="pool_phases")
    _closed = models.BooleanField(default=False)

    class Meta:
        unique_together = ["name", "tournament"]

    def add_players(self, players):
        for player in players:
            self.PP_players.add(player)

    def add_qualified_players(self, qualified_players):
        if not self._closed:
            self.__add_qualified_players(qualified_players)
            all_pools_finished = self.__check_all_pools()
            if all_pools_finished:
                self.__go_to_next_phase()

    def get_pools(self):
        return self.pools.all()

    def get_all_matches(self):
        matches = []
        for pool in self.get_pools():
            for match in pool.pool_matches.all():
                matches.append(match)
        return matches

    def __add_qualified_players(self, qualified_players):
        for player in qualified_players:
            self.PP_qualified_players.add(player)
        self.save()

    def enter_result(self, match, result, winner=None):
        pool = self.__get_pool_of_match(match)
        pool.enter_result(match=match, result=result, winner=winner)

    def __go_to_next_phase(self):
        self._closed = True
        self.__delete_all_phase_matches()
        self.save()
        self.tournament.go_to_next_phase(qualified_players=self.PP_qualified_players.all())

    def __delete_all_phase_matches(self):
        for pool in self.pools.all():
            pool.pool_matches.all().delete()

    def __check_all_pools(self):
        for pool in self.pools.all():
            if not pool.all_matches_played:
                return False
        return True

    def __get_pool_of_match(self, match):
        for pool in self.get_pools():
            for pool_match in pool.get_pool_matches():
                if match.id == pool_match.id:
                    return pool

    def get_players(self):
        return self.PP_players.all()

    def is_open(self):
        return not self._closed

    def get_players_count(self):
        return self.PP_players.count()

    def get_pool_of_player(self, player):
        for pool in self.pools.all():
            if pool in player.my_small_pools.all():
                return pool

    def __assign_matches_to_pools(self):
        for pool in self.pools.all():
            pool.create_matches()

    def __create_small_pools(self, groups_of_3, groups_of_4):
        not_yet_selected_players = {0}
        not_yet_selected_players.remove(0)
        not_yet_selected_players.update(self.PP_players.all())

        not_yet_selected_players = self.__create_new_pool(groups_of_4, 3, not_yet_selected_players)
        self.__create_new_pool(groups_of_3, 2, not_yet_selected_players)

    def __create_large_pools(self, groups_of_5, groups_of_6):
        not_yet_selected_players = {0}
        not_yet_selected_players.remove(0)
        not_yet_selected_players.update(self.PP_players.all())

        not_yet_selected_players = self.__create_new_pool(groups_of_6, 5, not_yet_selected_players)
        self.__create_new_pool(groups_of_5, 4, not_yet_selected_players)

    def __create_new_pool(self, num_of_groups, size, all_players):
        counter = 0
        while counter != num_of_groups:
            player = random.sample(all_players, 1)[0]
            forbidden_players = {0}
            forbidden_players.remove(0)
            forbidden_players.update(player.get_encountered_players())
            all_players.remove(player)
            non_encountered = all_players - forbidden_players
            number_of_choices = len(non_encountered)
            new_pool = Pool.objects.create(pool_phase=self)

            pool_players = []

            if number_of_choices >= size:
                pool_players = random.sample(non_encountered, size)
            elif number_of_choices > 0:
                diff = size - number_of_choices

                non_encountered_players = random.sample(non_encountered, number_of_choices)
                for non_encountered_player in non_encountered_players:
                    pool_players.append(non_encountered_player)

                all_other_players = []
                for player in all_players:
                    if player not in non_encountered_players:
                        all_other_players.append(player)

                encountered_players = random.sample(all_other_players, diff)
                for encountered_player in encountered_players:
                    pool_players.append(encountered_player)

            else:
                pool_players = random.sample(all_players, size)

            for new_player in pool_players:
                all_players.remove(new_player)

            pool_players.append(player)
            new_pool.add_players(pool_players)

            counter += 1

        return all_players

    def __generate_small_pool_schedule(self):
        number_of_players = self.PP_players.count()
        groups_of_3, groups_of_4 = self.__small_groups(number_of_players)
        self.__create_small_pools(groups_of_3, groups_of_4)
        self.__assign_matches_to_pools()
        return self.pools.all()

    def __small_groups(self, number_of_players):
        remainder = number_of_players % 4
        groups_of_4 = 0
        groups_of_3 = 0
        if remainder == 0:
            groups_of_4 = number_of_players // 4
        elif remainder == 1:
            groups_of_3 = 3
            groups_of_4 = (number_of_players - 9) // 4
        elif remainder == 2:
            groups_of_3 = 2
            groups_of_4 = (number_of_players - 6) // 4
        else:
            groups_of_3 = 1
            groups_of_4 = (number_of_players - 3) // 4

        return groups_of_3, groups_of_4

    def __large_groups(self, number_of_players):
        remainder = number_of_players % 5
        groups_of_5 = 0
        groups_of_6 = 0
        if remainder == 0:
            groups_of_5 = number_of_players // 5
        elif remainder == 1:
            groups_of_6 = 1
            groups_of_5 = (number_of_players - 6) // 5
        elif remainder == 2:
            groups_of_6 = 2
            groups_of_5 = (number_of_players - 12) // 5
        elif remainder == 3:
            groups_of_6 = 3
            groups_of_5 = (number_of_players - 18) // 5
        elif remainder == 4:
            groups_of_6 = 4
            groups_of_5 = (number_of_players - 24) // 5

        return groups_of_5, groups_of_6

    def __super_large_groups(self, number_of_players):
        remainder = number_of_players % 6
        groups_of_5 = 0
        groups_of_6 = 0
        if remainder == 0:
            groups_of_6 = number_of_players // 6
        elif remainder == 1:
            groups_of_5 = 5
            groups_of_6 = (number_of_players - 25) // 6
        elif remainder == 2:
            groups_of_5 = 4
            groups_of_6 = (number_of_players - 20) // 6
        elif remainder == 3:
            groups_of_5 = 3
            groups_of_6 = (number_of_players - 15) // 6
        elif remainder == 4:
            groups_of_5 = 2
            groups_of_6 = (number_of_players - 10) // 6
        else:
            groups_of_5 = 1
            groups_of_6 = (number_of_players - 5) // 6

        return groups_of_5, groups_of_6

    def __generate_large_pool_schedule(self):
        number_of_players = self.PP_players.count()
        groups_of_3 = 0
        groups_of_4 = 0
        groups_of_5 = 0
        groups_of_6 = 0
        if 33 <= number_of_players < 45:
            groups_of_3, groups_of_4 = self.__small_groups(number_of_players)
            self.__create_small_pools(groups_of_3, groups_of_4)
        elif 45 <= number_of_players <= 84:
            groups_of_5, groups_of_6 = self.__large_groups(number_of_players)
            self.__create_large_pools(groups_of_5, groups_of_6)
        elif 85 <= number_of_players <= 96:
            groups_of_5, groups_of_6 = self.__super_large_groups(number_of_players)
            self.__create_large_pools(groups_of_5, groups_of_6)

        self.__assign_matches_to_pools()
        return self.pools.all()

    def generate_schedule(self):
        if 17 <= self.PP_players.count() <= 32:
            return self.__generate_small_pool_schedule()
        elif 33 <= self.PP_players.count() <= 96:
            return self.__generate_large_pool_schedule()
        else:
            raise ValueError("The number of players is invalid")


class Pool(models.Model):
    pool_phase = models.ForeignKey(PoolPhase, on_delete=models.CASCADE, related_name="pools", null=True)
    all_matches_played = models.BooleanField(default=False)

    def get_players_count(self):
        return self.pool_players.count()

    def get_players(self):
        return self.pool_players.all()

    def get_pool_matches(self):
        return self.pool_matches.all()

    def add_players(self, players):
        for player in players:
            if player not in self.pool_phase.get_players():
                raise ValidationError("One of the players is not part of the tournament")
        for player in players:
            if player not in self.pool_players.all():
                self.pool_players.add(player)
        self.save()

    def create_matches(self):
        for i in range(self.pool_players.count()):
            for j in range(i + 1, self.pool_players.count()):
                player1 = self.pool_players.all()[i]
                player2 = self.pool_players.all()[j]
                new_match = PoolMatch.objects.create_pool_match(player1=player1, player2=player2,
                                                                tournament=self.pool_phase.tournament,
                                                                pool=self)
                self.pool_matches.add(new_match)
                self.save()

    def enter_result(self, match, result, winner=None):
        if not self.all_matches_played:
            match.enter_result(result, winner)
            self.__are_all_matches_played()
            if self.all_matches_played:
                self.__set_qualified_players()

    def enter_winner(self, winner, match):
        match.enter_winner(winner)
        self.__are_all_matches_played()
        if self.all_matches_played:
            self.__set_qualified_players()

    def enter_draw(self, match):
        match.enter_draw()
        self.__are_all_matches_played()
        if self.all_matches_played:
            self.__set_qualified_players()

    def __are_all_matches_played(self):
        self.all_matches_played = all(not m.is_open() for m in self.pool_matches.all())
        self.save()

    def __set_qualified_players(self):
        qualified_players = self.__get_qualified_players()
        self.pool_phase.add_qualified_players(qualified_players)

    def __get_qualified_players(self):
        return [self.pool_players.all()[0], self.pool_players.all()[1]]


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
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="tournament_schedule")

    objects = MatchManager()

    def get_player1(self):
        return self._player1

    def get_player2(self):
        return self._player2

    def enter_winner(self, player):
        if not self._open:
            raise ValidationError("This match is closed")
        if player == self._player1 or player == self._player2:
            self._winner = player
            self._player1.add_encountered_player(self._player2)
            self.__close_match()
            self.save()
            return self._winner
        else:
            raise ValueError("This player is not a player of this match")

    def enter_draw(self):
        if not self._open:
            raise ValidationError("This match is closed")
        else:
            self._player1.add_encountered_player(self._player2)
            self.__close_match()
            self.save()

    def __close_match(self):
        self._open = False

    def get_winner(self):
        return self._winner

    def get_loser(self):
        if self._winner:
            if self._winner == self._player1:
                return self._player2
            else:
                return self._player1

    def is_open(self):
        return self._open


class PoolMatchManager(MatchManager):

    def create_pool_match(self, tournament, player1, player2, pool):
        match = super().create_match(tournament, player1, player2)
        match.pool = pool
        match.save(using=self._db)
        return match


class PoolMatch(Match):
    pool = models.ForeignKey(Pool, on_delete=models.CASCADE, related_name="pool_matches")

    def enter_result(self, result, winner=None):
        if result:
            self.__enter_winner(winner)
        else:
            self.__enter_draw_result()

    def __enter_winner(self, winner):
        true_winner = super(PoolMatch, self).enter_winner(winner)
        self.__set_win_points(true_winner)
        self.save()

    def __enter_draw_result(self):
        super(PoolMatch, self).enter_draw()
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

    objects = PoolMatchManager()


class EliminationMatchManager(MatchManager):

    def create_elimination_match(self, tournament, player1, player2, elimination_round):
        match = super().create_match(tournament, player1, player2)
        match.elimination_round = elimination_round
        match.save(using=self._db)
        return match


class EliminationMatch(Match):
    elimination_round = models.ForeignKey(EliminationRounds, on_delete=models.CASCADE, related_name="schedule",
                                          null=True)

    def enter_winner(self, player):
        winner = super(EliminationMatch, self).enter_winner(player)
        loser = self.get_loser()
        self.elimination_round.remove_player(loser)
        return winner

    objects = EliminationMatchManager()
