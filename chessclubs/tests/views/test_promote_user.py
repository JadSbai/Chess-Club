from django.core.exceptions import ValidationError
from django.test import TestCase
from chessclubs.models import User
from django.contrib.auth.models import Group, Permission


class PromoteUserTestCase(TestCase):

    fixtures = [
        'chessclubs/tests/fixtures/default_user.json',
        'chessclubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.user.groups.clear()
        #self.user.groups.add(self.owner)

        self.target_user = User.objects.get(username='@janedoe')
        members.user_set.add(target_user)

    def test_promote_to_officer(self):
        pass
        #owner.user_set.add(self.user)



    def test_cannot_promote_when_not_owner(self):
        pass
