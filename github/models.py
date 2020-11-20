from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db.models.deletion import CASCADE

## ENUMERATIONS ##


class RepositoryRoleLevel(models.TextChoices):
    READ = "Read"
    TRIAGE = "Triage"
    WRITE = "Write"
    MAINTAIN = "Maintain"
    ADMIN = "Admin"


class OrganizationRoleLevel(models.TextChoices):
    MEMBER = "Member"
    BILLING_MANAGER = "Billing"
    OWNER = "Owner"


class TeamRoleLevel(models.TextChoices):
    MEMBER = "Member"
    MAINTAINER = "Maintainer"


## MODELS ##


class Organization(models.Model):
    name = models.CharField(max_length=1024)
    base_role = models.CharField(
        max_length=256,
        choices=RepositoryRoleLevel.choices,
        default=RepositoryRoleLevel.READ,
    )

    def __str__(self):
        return f"{self.name}"


class User(AbstractUser):
    # basic info
    email = models.CharField(max_length=256)


class Team(models.Model):
    name = models.CharField(max_length=1024)

    # many-to-one relationship with organizations
    organization = models.ForeignKey(Organization, CASCADE)

    # many-to-one relationship with team maintainer
    team_maintainer = models.ForeignKey(
        User, on_delete=models.RESTRICT, related_name="maintainer_teams"
    )

    # many-to-many relationship with team members (Users)
    users = models.ManyToManyField(User, related_name="member_teams")

    def __str__(self):
        return f"{self.name}"


class Repository(models.Model):
    name = models.CharField(max_length=1024)
    # many-to-one relationship with organizations
    organization = models.ForeignKey(Organization, CASCADE)

    # time info
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"


class Issue(models.Model):
    name = models.CharField(max_length=1024)
    # many-to-one relationship with repositories
    repository = models.ForeignKey(Repository, CASCADE)

    def __str__(self):
        return f"{self.name}"


## ROLE MODELS ##


class RepositoryRole(models.Model):
    # RepositoryRole name, selected from RepositoryRoleChoices
    name = models.CharField(max_length=256, choices=RepositoryRoleLevel.choices)

    # many-to-one relationship with repositories
    repository = models.ForeignKey(Repository, CASCADE)

    # many-to-many relationship with users
    users = models.ManyToManyField(User, blank=True)

    # many-to-many relationship with teams
    teams = models.ManyToManyField(Team, blank=True)

    def __str__(self):
        return f"{RepositoryRoleLevel(self.name).label} on {self.repository}"


class OrganizationRole(models.Model):
    # Role name, selected from role choices
    name = models.CharField(max_length=256, choices=OrganizationRoleLevel.choices)

    # many-to-one relationship with organizations
    organization = models.ForeignKey(Organization, CASCADE)

    # many-to-many relationship with users
    users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return f"{OrganizationRoleLevel(self.name).label} of {self.organization}"
