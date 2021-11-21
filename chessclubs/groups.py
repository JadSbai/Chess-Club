"""Python file where groups are created and permissions assigned to these groups (applicant, member, officer, owner)"""
from django.contrib.auth.models import Group, Permission

groups = {}  # Dictionary of groups

def create_groups():
    """Create the groups for the app"""
    applicants, created = Group.objects.get_or_create(name="applicants")
    groups["applicants"] = applicants
    members, created2 = Group.objects.get_or_create(name="members")
    groups["members"] = members
    officers, created3 = Group.objects.get_or_create(name="officers")
    groups["officers"] = officers
    owner, created4 = Group.objects.get_or_create(name="owner")
    groups["owner"] = owner
    denied_applicants, created5 = Group.objects.get_or_create(name="denied_applicants")
    groups["denied_applicants"] = denied_applicants

def assign_permissions():
    """Get the permissions from the User model's Meta class and assign them to the groups"""
    members_list = Permission.objects.get(codename='access_members_list')
    public = Permission.objects.get(codename='show_public_info')
    members_permissions = [members_list, public]
    groups["members"].permissions.set(members_permissions)
    private = Permission.objects.get(codename='show_private_info')
    officers_permissions = [members_list, public, private]
    groups["officers"].permissions.set(officers_permissions)
    promote = Permission.objects.get(codename='promote')
    demote = Permission.objects.get(codename='demote')
    transfer_ownership = Permission.objects.get(codename='transfer_ownership')
    owner_permissions = [members_list, public, private, promote, demote, transfer_ownership]
    groups["owner"].permissions.set(owner_permissions)


def set_up_app_groups():
    """Set up the app's groups and their permissions"""
    create_groups()
    assign_permissions()
    return groups
