# Generated by Django 3.2.5 on 2021-12-08 19:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chessclubs', '0014_auto_20211208_1832'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='_winner',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='won_matches', to=settings.AUTH_USER_MODEL),
        ),
    ]