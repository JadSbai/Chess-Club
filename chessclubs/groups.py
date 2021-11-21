from django.contrib.auth.models import Group, Permission

applicants, created = Group.objects.get_or_create(name="applicants")
members, created2 = Group.objects.get_or_create(name="members")
officers, created3 = Group.objects.get_or_create(name="officers")
owner, created4 = Group.objects.get_or_create(name="owner")
denied_applicants, created5 = Group.objects.get_or_create(name="denied_applicants")

membersList = Permission.objects.get(codename='access_members_list')
public = Permission.objects.get(codename='show_public_info')
private = Permission.objects.get(codename='show_private_info')
promote = Permission.objects.get(codename='promote')
demote = Permission.objects.get(codename='demote')
transfer_ownership = Permission.objects.get(codename='transfer_ownership')
manage_applications = Permission.objects.get(codename='manage_applications')

members_permissions = [public, membersList]
officers_permissions = members_permissions + [private, manage_applications]
owner_permissions = [promote, demote, transfer_ownership, public, membersList, private]

members.permissions.set(members_permissions)
officers.permissions.set(officers_permissions)
owner.permissions.set(owner_permissions)
