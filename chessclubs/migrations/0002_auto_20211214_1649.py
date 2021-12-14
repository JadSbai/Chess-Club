# Generated by Django 3.2.8 on 2021-12-14 16:49

import chessclubs.models
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('chessclubs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tournament',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('description', models.CharField(max_length=240)),
                ('location', models.CharField(max_length=50)),
                ('max_capacity', models.IntegerField(default=2, validators=[django.core.validators.MaxValueValidator(96, 'The max capacity needs to be less than 96.'), django.core.validators.MinValueValidator(2, 'The max capacity needs to be at least 2.')])),
                ('deadline', models.DateTimeField(validators=[chessclubs.models.validate_tournament_deadline])),
            ],
            options={
                'permissions': [('play_matches', 'Can play matches'), ('enter_match_results', 'Can enter match results'), ('see_tournament_private_info', 'Can see tournament private info')],
            },
        ),
        migrations.AlterModelOptions(
            name='club',
            options={'permissions': [('access_members_list', 'Can access the list of members'), ('show_public_info', "Can access a member's public info"), ('show_private_info', "Can access a member's private info"), ('promote', 'Can promote members'), ('demote', 'Can demote officers'), ('transfer_ownership', 'Can transfer ownership to an officer'), ('manage_applications', 'Can manage applications'), ('access_club_info', "Can access a club's public info"), ('access_club_owner_public_info', 'Can access a club owner public info'), ('acknowledge_response', 'Can acknowledge response (acceptance or denial) to an application'), ('apply_to_club', 'Can apply to club'), ('ban', 'Can ban a user from the club'), ('leave', 'Can leave a club'), ('create_tournament', 'Can create a tournament'), ('apply_tournament', 'Can apply to a tournament'), ('withdraw_tournament', 'Can withdraw from a tournament'), ('edit_club_info', 'Can edit club information')]},
        ),
        migrations.CreateModel(
            name='TournamentPermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('base_permission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tournament_permission', to='auth.permission')),
                ('groups', models.ManyToManyField(related_name='tournament_permissions', to='auth.Group')),
                ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chessclubs.tournament')),
                ('users', models.ManyToManyField(related_name='user_tournament_permissions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='tournament',
            name='club',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='all_tournaments', to='chessclubs.club'),
        ),
        migrations.AddField(
            model_name='tournament',
            name='co_organisers',
            field=models.ManyToManyField(related_name='co_organised_tournaments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='tournament',
            name='organiser',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='organised_tournaments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='tournament',
            name='participants',
            field=models.ManyToManyField(related_name='tournaments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='tournamentpermission',
            index=models.Index(fields=['tournament', 'base_permission'], name='chessclubs__tournam_556660_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='tournamentpermission',
            unique_together={('tournament', 'base_permission')},
        ),
    ]
