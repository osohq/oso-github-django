from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db.models.deletion import CASCADE
from enum import Enum

## ENUMERATIONS ##


class RepositoryRoleChoices(Enum):
    READ = "Read"
    TRIAGE = "Triage"
    WRITE = "Write"
    MAINTAIN = "Maintain"
    ADMIN = "Admin"


class OrganizationRoleChoices(Enum):
    MEMBER = "Member"
    BILLING = "Billing Manager"
    OWNER = "Owner"


## MODELS ##


class Organization(models.Model):
    name = models.CharField(max_length=1024)
    base_role = models.CharField(
        max_length=256, choices=[(tag, tag.value) for tag in RepositoryRoleChoices]
    )


class User(AbstractUser):
    # many-to-many relationship with organizations
    organizations = models.ManyToManyField(Organization)

    # basic info
    email = models.CharField(max_length=256)


class Team(models.Model):
    # many-to-one relationship with organizations
    organization = models.ForeignKey(Organization, CASCADE)

    # many-to-one relationship with team maintainer
    team_maintainer = models.ForeignKey(
        User, on_delete=models.RESTRICT, related_name="maintainer_teams"
    )

    # many-to-many relationship with team members (Users)
    users = models.ManyToManyField(User, related_name="member_teams")


class Repository(models.Model):
    # many-to-one relationship with organizations
    organization = models.ForeignKey(Organization, CASCADE)

    # time info
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Issue(models.Model):
    # many-to-one relationship with repositories
    repository = models.ForeignKey(Repository, CASCADE)


## ROLE MODELS ##


class RepositoryRole(models.Model):
    # RepositoryRole name, selected from RepositoryRoleChoices
    name = models.CharField(
        max_length=256, choices=[(tag, tag.value) for tag in RepositoryRoleChoices]
    )

    # many-to-one relationship with organizations
    # TODO: do we actually need the organization to be on the role?
    organization = models.ForeignKey(Organization, CASCADE)

    # many-to-one relationship with repositories
    repository = models.ForeignKey(Repository, CASCADE)

    # many-to-many relationship with users
    users = models.ManyToManyField(User)

    # many-to-many relationship with teams
    teams = models.ManyToManyField(Team)


class AdminRole(models.Model):
    # Role name, selected from role choices
    name = models.CharField(
        max_length=256, choices=[(tag, tag.value) for tag in OrganizationRoleChoices]
    )

    # many-to-one relationship with organizations
    # TODO: do we actually need the organization to be on the role?
    organization = models.ForeignKey(Organization, CASCADE)
