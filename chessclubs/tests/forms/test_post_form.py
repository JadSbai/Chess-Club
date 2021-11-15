from django.test import TestCase
from chessclubs.models import User, Post
from chessclubs.forms import PostForm

class PostFormTestCase(TestCase):

    fixtures = ['chessclubs/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')

    def test_valid_post_form(self):
        input = {'text': 'x'*200 }
        form = PostForm(data=input)
        self.assertTrue(form.is_valid())

    def test_invalid_post_form(self):
        input = {'text': 'x'*600 }
        form = PostForm(data=input)
        self.assertFalse(form.is_valid())
