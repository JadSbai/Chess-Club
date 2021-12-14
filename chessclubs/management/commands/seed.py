"""The database seeder."""
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from faker import Faker
import random
from chessclubs.models import User, Club, Tournament
from django.utils import timezone
from chessclubs.tests.helpers import enter_results_to_all_matches


class Command(BaseCommand):
    PASSWORD = "Password123"
    USER_SIZE = 50
    CLUB_SIZE = 10
    TOURNAMENT_SIZE = 5
    JEB = None
    BILLIE = None
    VALENTINA = None
    CLUB1OWNER = None
    CLUB3OWNER = None
    KERBAL = None
    RANDOM_USERS_LIST = []
    SPECIFIC_USERS_LIST = []
    SPECIFIC_CLUBS_LIST = []

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        user_count = 0
        club_count = 0
        tournament_count = 0

        try:
            Command.JEB = self._create_specific_user('Jebediah', 'Kerman', 'jeb@example.org')
            Command.VALENTINA = self._create_specific_user('Valentina', 'Kerman', 'val@example.org')
            Command.BILLIE = self._create_specific_user('Billie', 'Kerman', 'billie@example.org')
            Command.CLUB1OWNER = self._create_specific_user('Club 1', 'Owner', 'club1owner@example.org')
            Command.CLUB3OWNER = self._create_specific_user('Club 3', 'Owner', 'club3owner@example.org')
            Command.SPECIFIC_USERS_LIST = [Command.CLUB3OWNER, Command.CLUB1OWNER, Command.BILLIE, Command.VALENTINA,
                                           Command.JEB]
            user_count += 3
        except IntegrityError:
            print("You have already created the specific users")

        try:
            kerbal = self._create_specific_club('Kerbal Chess Club', 'Description', 'London', 'billie@example.org')
            Command.KERBAL = kerbal
            club1 = self._create_specific_club('Club 1', 'Description 1', 'London', 'club1owner@example.org')
            club2 = self._create_specific_club('Club 2', 'Description 2', 'London', 'val@example.org')
            club3 = self._create_specific_club('Club 3', 'Description 3', 'London', 'club3owner@example.org')
            Command.SPECIFIC_CLUBS_LIST = [kerbal, club1, club2, club3]
            club_count += 4
            kerbal.add_member(Command.JEB)
            kerbal.members.add(Command.VALENTINA)
            kerbal.add_to_officers_group(Command.VALENTINA)
            club1.members.add(Command.JEB)
            club1.add_to_officers_group(Command.JEB)
            club3.add_member(Command.BILLIE)
            kerbal.add_to_logged_in_non_members_group(Command.CLUB1OWNER)
            kerbal.add_to_logged_in_non_members_group(Command.CLUB3OWNER)
            club1.add_to_logged_in_non_members_group(Command.CLUB3OWNER)
            club1.add_to_logged_in_non_members_group(Command.VALENTINA)
            club1.add_to_logged_in_non_members_group(Command.BILLIE)
            club2.add_to_logged_in_non_members_group(Command.CLUB1OWNER)
            club2.add_to_logged_in_non_members_group(Command.CLUB3OWNER)
            club2.add_to_logged_in_non_members_group(Command.BILLIE)
            club2.add_to_logged_in_non_members_group(Command.JEB)
            club3.add_to_logged_in_non_members_group(Command.VALENTINA)
            club3.add_to_logged_in_non_members_group(Command.JEB)
            club3.add_to_logged_in_non_members_group(Command.CLUB1OWNER)
        except IntegrityError:
            print("You have already created the specific clubs")

        while user_count < Command.USER_SIZE:
            try:
                user = self._create_user()
                Command.RANDOM_USERS_LIST.append(user)
                user_count += 1
            except IntegrityError:
                print("This user already exists")
                continue

        while club_count < Command.CLUB_SIZE:
            try:
                club = self._create_club()
                self._assign_random_users_to_club_groups(club)
                self._assign_existing_users_to_non_logged_in_group(club)
                club_count += 1
            except IntegrityError:
                print("This club already exists")
                continue

        for club in Command.SPECIFIC_CLUBS_LIST:
            self._assign_random_users_to_club_groups(club)
            self._assign_existing_users_to_non_logged_in_group(club)

        try:
            deadline1 = timezone.now() - timezone.timedelta(days=1)
            deadline2 = timezone.now() - timezone.timedelta(days=2)
            deadline3 = timezone.now() - timezone.timedelta(days=3)
            deadline4 = timezone.now() - timezone.timedelta(days=4)
            deadline5 = timezone.now() - timezone.timedelta(days=5)
            tournament1 = Tournament.objects.create(name="Kerbal_Cup_1", description="First tournament",
                                                    location="London",
                                                    max_capacity=96, deadline=deadline1, organiser=Command.VALENTINA,
                                                    club=Command.KERBAL)
            self.assign_random_members_to_tournament(tournament1, forbidden=Command.JEB)
            tournament1.start_tournament()
            self.enter_results_until_finished(tournament1)

            tournament2 = Tournament.objects.create(name="Kerbal_Cup_2", description="Second tournament",
                                                    location="London",
                                                    max_capacity=32, deadline=deadline2, organiser=Command.VALENTINA,
                                                    club=Command.KERBAL)
            tournament2.add_participant(Command.JEB)
            self.assign_random_members_to_tournament(tournament2, forbidden=Command.JEB)

            tournament3 = Tournament.objects.create(name="Kerbal_Cup_3", description="Third tournament",
                                                    location="London",
                                                    max_capacity=16, deadline=deadline3, organiser=Command.VALENTINA,
                                                    club=Command.KERBAL)
            self.assign_random_members_to_tournament(tournament3)
            tournament3.start_tournament()

            tournament4 = Tournament.objects.create(name="Kerbal_Cup_4", description="Fourth tournament",
                                                    location="London",
                                                    max_capacity=55, deadline=deadline4, organiser=Command.VALENTINA,
                                                    club=Command.KERBAL)
            self.assign_random_members_to_tournament(tournament4)
            tournament4.start_tournament()

            tournament5 = Tournament.objects.create(name="Kerbal_Cup_5", description="Fifth tournament",
                                                    location="London",
                                                    max_capacity=38, deadline=deadline5, organiser=Command.VALENTINA,
                                                    club=Command.KERBAL)
            self.assign_random_members_to_tournament(tournament5)
            tournament5.start_tournament()

            tournament_count += 5
        except IntegrityError:
            print("You have already created the specific tournaments")

        print(f'Seeding complete: {club_count} clubs, {user_count} users, and {tournament_count} tournaments')

    def _create_user(self):
        """Creating generic user."""

        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = self._email(first_name, last_name)
        user = self._create_user_instance(first_name, last_name, email)
        return user

    def assign_random_members_to_tournament(self, tournament, forbidden=None):
        for member in tournament.club.get_members():
            if not tournament.is_organiser(member) and not tournament.is_max_capacity_reached() and member != forbidden:
                tournament.add_participant(member)

    def _create_club(self):
        name = self.faker.company()
        location = self.faker.city()
        description = self.faker.text(max_nb_chars=520)
        owner = random.choice(Command.RANDOM_USERS_LIST)
        club = Club.objects.create(name=name, location=location, description=description, owner=owner)
        club.members.add(owner)
        club.assign_club_groups_permissions()
        for specific_user in Command.SPECIFIC_USERS_LIST:
            club.add_to_logged_in_non_members_group(specific_user)
        return club

    def enter_results_until_finished(self, tournament):
        while not tournament._finished:
            enter_results_to_all_matches(tournament)
            tournament.refresh_from_db()

    def _create_specific_user(self, first_name, last_name, email):
        """Creating users specified in requirements with different roles for testing purposes."""
        user = self._create_user_instance(first_name, last_name, email)
        return user

    def _create_specific_club(self, name, description, location, owner_email):
        owner = User.objects.get(email=owner_email)
        club = Club.objects.create(name=name, description=description, location=location, owner=owner)
        club.members.add(owner)
        club.assign_club_groups_permissions()
        return club

    def _create_user_instance(self, first_name, last_name, email):
        bio = self.faker.text(max_nb_chars=520)
        chess_experience = self.faker.word(ext_word_list=['Novice', 'Beginner', 'Intermediate', 'Advanced', 'Expert'])
        personal_statement = self.faker.text(max_nb_chars=500)

        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            chess_experience=chess_experience,
            bio=bio,
            personal_statement=personal_statement,
            password=Command.PASSWORD
        )
        return user

    def _assign_random_users_to_club_groups(self, club):
        GROUP_CHOICES = club.get_seeder_groups()
        for user in Command.RANDOM_USERS_LIST:
            group = random.choice(GROUP_CHOICES)
            if user == club.owner:
                continue
            elif group == "applicant":
                club.add_to_applicants_group(user)
            elif group == "officer":
                club.members.add(user)
                club.add_to_officers_group(user)
            elif group == "member":
                club.add_member(user)
            elif group == "logged_in_non_member":
                club.add_to_logged_in_non_members_group(user)
            else:
                print("No group assigned")

    def _assign_existing_users_to_non_logged_in_group(self, club):
        for user in User.objects.all():
            if not (user in Command.RANDOM_USERS_LIST or user in Command.SPECIFIC_USERS_LIST):
                club.add_to_logged_in_non_members_group(user)

    def _email(self, first_name, last_name):
        email = '' + first_name.lower() + '.' + last_name.lower() + '@example.org'
        return email
