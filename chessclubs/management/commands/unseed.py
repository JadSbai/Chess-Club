"""The database unseeder."""
from django.core.management.base import BaseCommand, CommandError
from chessclubs.models import User, Club
from django.contrib.auth.models import Group

class Command(BaseCommand):
    def handle(self, *args, **options):
        User.objects.filter(is_staff=False, is_superuser=False).delete()
        Club.objects.all().delete()
        Group.objects.all().delete()

