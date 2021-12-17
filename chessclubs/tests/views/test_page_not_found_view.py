from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from chessclubs.models import User, Club
from chessclubs.tests.helpers import reverse_with_next

class PageNotFoundView(TestCase):

    def setUp(self):
        self.url='/club/blabla/'

    def test_get_page_not_found(self):
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, '404.html')
        self.assertEqual(response.status_code, 404)
