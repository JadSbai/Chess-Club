# Generated by Django 3.2.5 on 2021-11-30 21:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('bio', models.CharField(blank=True, max_length=520)),
                ('chess_experience', models.CharField(choices=[('Novice', 'Novice'), ('Beginner', 'Beginner'), ('Intermediate', 'Intermediate'), ('Advanced', 'Advanced'), ('Expert', 'Expert')], default='novice', max_length=50)),
                ('personal_statement', models.CharField(max_length=500)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Club',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('location', models.CharField(max_length=50)),
                ('description', models.CharField(blank=True, max_length=520)),
                ('members', models.ManyToManyField(related_name='clubs', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': [('access_members_list', 'Can access the list of members'), ('show_public_info', "Can access a member's public info"), ('show_private_info', "Can access a member's private info"), ('promote', 'Can promote members'), ('demote', 'Can demote officers'), ('transfer_ownership', 'Can transfer ownership to an officer'), ('manage_applications', 'Can manage applications'), ('access_club_info', "Can access a club's public info"), ('access_club_owner_public_info', 'Can access a club owner public info'), ('acknowledge_denial', 'Can acknowledge denial of application')],
            },
        ),
        migrations.CreateModel(
            name='ClubPermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('base_permission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='club_permission', to='auth.permission')),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chessclubs.club')),
                ('groups', models.ManyToManyField(related_name='club_permissions', to='auth.Group')),
                ('users', models.ManyToManyField(related_name='user_club_permissions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddIndex(
            model_name='clubpermission',
            index=models.Index(fields=['club', 'base_permission'], name='chessclubs__club_id_da7704_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='clubpermission',
            unique_together={('club', 'base_permission')},
        ),
    ]
