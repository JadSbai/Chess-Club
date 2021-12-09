# Generated by Django 3.2.5 on 2021-12-08 12:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chessclubs', '0008_auto_20211207_1807'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupStage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_player1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matches', to=settings.AUTH_USER_MODEL)),
                ('_player2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('_winner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='won_matches', to=settings.AUTH_USER_MODEL)),
                ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tournament_matches', to='chessclubs.tournament')),
            ],
        ),
        migrations.CreateModel(
            name='EliminationRounds',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_phase', models.CharField(choices=[('Final', 'Final'), ('Semi-Final', 'Semi-Final'), ('Quarter-Final', 'Quarter_Final'), ('Eight-Final', 'Eight-Final')], default='Eight_Final', max_length=50)),
                ('_players', models.ManyToManyField(related_name='elimination_rounds', to=settings.AUTH_USER_MODEL)),
                ('_small_group_stage', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='elimination_round', to='chessclubs.groupstage')),
                ('_tournament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chessclubs.tournament')),
            ],
        ),
    ]