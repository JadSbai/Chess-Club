# Generated by Django 3.2.5 on 2021-11-26 17:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chessclubs', '0013_auto_20211126_1437'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='club',
            name='applicants_group',
        ),
        migrations.RemoveField(
            model_name='club',
            name='authenticated_non_member_group',
        ),
        migrations.RemoveField(
            model_name='club',
            name='denied_applicants_group',
        ),
        migrations.RemoveField(
            model_name='club',
            name='members_group',
        ),
        migrations.RemoveField(
            model_name='club',
            name='officers_group',
        ),
    ]
