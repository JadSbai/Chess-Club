from django.contrib.auth.models import Group, Permission

applicants, created = Group.objects.get_or_create(name="applicants")
members, created2 = Group.objects.get_or_create(name="members")
officers, created3 = Group.objects.get_or_create(name="officers")

membersList = Permission.objects.get(codename='access_members_list')
public = Permission.objects.get(codename='show_public_info')
private = Permission.objects.get(codename='show_private_info')
promote = Permission.objects.get(codename='promote')
demote = Permission.objects.get(codename='demote')
transfer_ownership = Permission.objects.get(codename='transfer_ownership')

members_permissions = [public, membersList]
officers_permissions = members_permissions + [private]
owner_permissions = officers_permissions + [promote, demote, transfer_ownership]

members.permissions.set(members_permissions)
officers.permissions.set(officers_permissions)

