"""Python file where groups are created and permissions assigned to these groups"""

from django.contrib.auth.models import Group, Permission
from django.db import OperationalError

groups = {}  # Dictionary of groups


def create_groups():
    """Create the groups for the app"""
    # The boolean variables named with "created" store whether the group has been successfully created or not
    authenticated_non_member_users, non_member_user_created = Group.objects.get_or_create(name="authenticated_non_member_users")
    groups["authenticated_non_member_users"] = authenticated_non_member_users
    applicants, applicants_created = Group.objects.get_or_create(name="applicants")
    groups["applicants"] = applicants
    denied_applicants, denied_applicants_created = Group.objects.get_or_create(name="denied_applicants")
    groups["denied_applicants"] = denied_applicants
    members, members_created = Group.objects.get_or_create(name="members")
    groups["members"] = members
    officers, officers_created = Group.objects.get_or_create(name="officers")
    groups["officers"] = officers
    owner, owner_created = Group.objects.get_or_create(name="owner")
    groups["owner"] = owner


def assign_permissions():
    """Get the permissions from the User model's Meta class and assign them to the groups"""
    # Get the permissions
    access_club_info = Permission.objects.get(codename="access_club_info")
    access_club_owner_info = Permission.objects.get(codename="access_club_owner_public_info")
    members_list = Permission.objects.get(codename='access_members_list')
    public = Permission.objects.get(codename='show_public_info')
    private = Permission.objects.get(codename='show_private_info')
    manage_applications = Permission.objects.get(codename='manage_applications')
    promote = Permission.objects.get(codename='promote')
    demote = Permission.objects.get(codename='demote')
    transfer_ownership = Permission.objects.get(codename='transfer_ownership')
    # Create sets of permissions
    logged_in_non_members_permissions = [access_club_info, access_club_owner_info]
    applicants_permissions = [access_club_info, access_club_owner_info]
    denied_applicants_permissions = [access_club_info, access_club_owner_info]
    members_permissions = [members_list, public, access_club_owner_info, access_club_info]
    officers_permissions = [members_list, public, private, manage_applications, access_club_owner_info, access_club_info]
    owner_permissions = [members_list, public, private, promote, demote, transfer_ownership, access_club_owner_info, access_club_info, manage_applications]
    # Assign the permissions to the groups
    groups["authenticated_non_member_users"].permissions.set(logged_in_non_members_permissions)
    groups["applicants"].permissions.set(applicants_permissions)
    groups["denied_applicants"].permissions.set(denied_applicants_permissions)
    groups["members"].permissions.set(members_permissions)
    groups["officers"].permissions.set(officers_permissions)
    groups["owner"].permissions.set(owner_permissions)


def set_up_app_groups():
    """Set up the app's groups and their permissions if migrations have been applied to the database"""
    try:
        create_groups()
        assign_permissions()
    # Catch any operational database exception in case the migrations have not yet been applied
    except:
        print("Will apply the migrations to the database")
    return groups
