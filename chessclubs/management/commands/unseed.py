"""The database unseeder."""
from django.core.management.base import BaseCommand, CommandError
from chessclubs.models import User

class Command(BaseCommand):
    def handle(self, *args, **options):
        User.objects.filter(is_staff=False, is_superuser=False).delete()
