"""The database seeder."""
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from faker import Faker
from django.contrib.auth.models import Group
import random
from chessclubs.models import UserManager, User
from chessclubs.groups import members, officers, applicants, owner, denied_applicants

class Command(BaseCommand):
    PASSWORD = "Password123"
    USER_SIZE = 50

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        user_count = 0 # users created so far
        while user_count < Command.USER_SIZE:
            try:
                self._create_user()
                user_count += 1
            except IntegrityError:
                continue
        try:
            self._create_specific_user('Jebediah', 'Kerman', 'jeb@example.org', members)
            self._create_specific_user('Valentina', 'Kerman', 'val@example.org', officers)
            self._create_specific_user('Billie', 'Kerman', 'billie@example.org', owner)
        except IntegrityError:
            pass
        print(f'User seeding complete.')

    def _create_user(self):
        """Creating generic user."""

        first_name=self.faker.first_name()
        last_name=self.faker.last_name()
        email=self._email(first_name, last_name)
        user = self._create_user_instance(first_name, last_name, email)
        self._assign_user_to_random_group(user)

    def _create_specific_user(self, first_name, last_name, email, group_name):
        """Creating users specified in requirements with different roles for testing purposes."""

        user = self._create_user_instance(first_name, last_name, email)
        self._assign_user_to_specific_group(user, group_name)

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

    def _assign_user_to_random_group(self, user):
        current_groups=list(Group.objects.exclude(name='owner'))
        group_name=random.choice(current_groups)
        user.groups.add(group_name)

    def _assign_user_to_specific_group(self, user, group_name):
        user.groups.add(group_name)

    def _email(self, first_name, last_name):
        email = '' + first_name.lower() + '.' + last_name.lower() + '@example.org'
        return email
