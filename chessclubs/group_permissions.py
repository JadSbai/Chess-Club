from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import User

applicants = Group.objects.create(name="applicants")
members = Group.objects.create(name="members")
officers = Group.objects.create(name="officers")


user_type = ContentType.objects.get_for_model(User)
members_list = Permission.objects.create(
    codename='access_members_list',
    name='Can Access the Members List',
    content_type=user_type,
)

show_public_info = Permission.objects.create(
    codename='show_public_info',
    name='Can Access Members Public Info',
    content_type=user_type,
)

show_private_info = Permission.objects.create(
    codename='show_private_info',
    name='Can Access Members Private Info',
    content_type=user_type,
)

promote = Permission.objects.create(
    codename='promote',
    name='Can Promote',
    content_type=user_type,
)

demote = Permission.objects.create(
    codename='demote',
    name='Can Demote',
    content_type=user_type,
)

transfer_ownership = Permission.objects.create(
    codename='transfer_ownership',
    name='Can Transfer Ownership',
    content_type=user_type,
)

members_permissions = [members_list, show_public_info]
officers_permissions = members_permissions + [show_private_info]
owner_permissions = officers_permissions + [promote, demote, transfer_ownership]

members.permissions.add(members_list)
officers.permissions.set(officers_permissions)
