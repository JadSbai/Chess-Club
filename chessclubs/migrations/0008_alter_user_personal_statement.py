# Generated by Django 3.2.5 on 2021-11-22 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chessclubs', '0007_alter_user_managers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='personal_statement',
            field=models.CharField(max_length=500),
        ),
    ]
