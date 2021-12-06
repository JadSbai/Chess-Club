# Generated by Django 3.2.5 on 2021-12-06 00:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chessclubs', '0003_auto_20211204_1114'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='club',
            options={'permissions': [('access_members_list', 'Can access the list of members'), ('show_public_info', "Can access a member's public info"), ('show_private_info', "Can access a member's private info"), ('promote', 'Can promote members'), ('demote', 'Can demote officers'), ('transfer_ownership', 'Can transfer ownership to an officer'), ('manage_applications', 'Can manage applications'), ('access_club_info', "Can access a club's public info"), ('access_club_owner_public_info', 'Can access a club owner public info'), ('acknowledge_response', 'Can acknowledge response (acceptance or denial) to an application'), ('apply_to_club', 'Can apply to club'), ('ban', 'Can ban a user from the club')]},
        ),
    ]
