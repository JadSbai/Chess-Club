"""The database seeder."""
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from faker import Faker
import random
from chessclubs.models import User, Club


class Command(BaseCommand):
    PASSWORD = "Password123"
    USER_SIZE = 50
    CLUB_SIZE = 10
    JEB = None
    BILLIE = None
    VALENTINA = None
    CLUB1OWNER = None
    CLUB3OWNER = None
    RANDOM_USERS_LIST = []
    SPECIFIC_USERS_LIST = []
    SPECIFIC_CLUBS_LIST = []

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        user_count = 0 # users created so far
        club_count = 0

        try:
            Command.JEB = self._create_specific_user('Jebediah', 'Kerman', 'jeb@example.org')
            Command.VALENTINA = self._create_specific_user('Valentina', 'Kerman', 'val@example.org')
            Command.BILLIE = self._create_specific_user('Billie', 'Kerman', 'billie@example.org')
            Command.CLUB1OWNER = self._create_specific_user('Club 1', 'Owner', 'club1owner@example.org')
            Command.CLUB3OWNER = self._create_specific_user('Club 3', 'Owner', 'club3owner@example.org')
            Command.SPECIFIC_USERS_LIST = [Command.CLUB3OWNER, Command.CLUB1OWNER, Command.BILLIE, Command.VALENTINA, Command.JEB]
            user_count += 3
        except IntegrityError:
            print("You have already created the specific users")

        try:
            kerbal = self._create_specific_club('Kerbal Chess Club', 'Description', 'London', 'billie@example.org')
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
        print(f'Seeding complete: {club_count} clubs and {user_count} users')

    def _create_user(self):
        """Creating generic user."""

        first_name=self.faker.first_name()
        last_name=self.faker.last_name()
        email=self._email(first_name, last_name)
        user = self._create_user_instance(first_name, last_name, email)
        return user

    def _create_club(self):
        name=self.faker.company()
        location=self.faker.city()
        description=self.faker.text(max_nb_chars=520)
        owner=random.choice(Command.RANDOM_USERS_LIST)
        club = Club.objects.create(name=name, location=location,description=description,owner=owner)
        club.members.add(owner)
        club.assign_club_groups_permissions()
        for specific_user in Command.SPECIFIC_USERS_LIST:
            club.add_to_logged_in_non_members_group(specific_user)
        return club

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
        bio=self.faker.text(max_nb_chars=520)
        chess_experience=self.faker.word(ext_word_list = ['Novice', 'Beginner', 'Intermediate', 'Advanced', 'Expert'])
        personal_statement=self.faker.text(max_nb_chars=500)

        user=User.objects.create_user(
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
            group=random.choice(GROUP_CHOICES)
            if user == club.owner:
                continue
            elif group == "applicant":
                club.members.add(user)
                club.add_to_applicants_group(user)
            elif group == "officer":
                club.members.add(user)
                club.add_to_officers_group(user)
            elif group == "member":
                club.add_member(user)
            elif group == "logged_in_non_member":
                club.add_to_logged_in_non_members_group(user)
            else: print("No group assigned")

    def _assign_existing_users_to_non_logged_in_group(self, club):
        for user in User.objects.all():
            if not (user in Command.RANDOM_USERS_LIST or user in Command.SPECIFIC_USERS_LIST):
                club.add_to_logged_in_non_members_group(user)

    def _email(self, first_name, last_name):
        email = '' + first_name.lower() + '.' + last_name.lower() + '@example.org'
        return email
