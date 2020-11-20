from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db.models.deletion import CASCADE

from django_oso.models import AuthorizedModel

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


class Organization(AuthorizedModel):
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

    organizations = models.ManyToManyField(Organization)


class Team(AuthorizedModel):
    name = models.CharField(max_length=1024)

    # many-to-one relationship with organizations
    organization = models.ForeignKey(Organization, CASCADE)

    def __str__(self):
        return f"{self.name}"


class Repository(AuthorizedModel):
    name = models.CharField(max_length=1024)
    # many-to-one relationship with organizations
    organization = models.ForeignKey(Organization, CASCADE)

    # time info
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"


class Issue(AuthorizedModel):
    name = models.CharField(max_length=1024)
    # many-to-one relationship with repositories
    repository = models.ForeignKey(Repository, CASCADE)

    def __str__(self):
        return f"{self.name}"


## ROLE MODELS ##


class RepositoryRole(AuthorizedModel):
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


class OrganizationRole(AuthorizedModel):
    # Role name, selected from role choices
    name = models.CharField(max_length=256, choices=OrganizationRoleLevel.choices)

    # many-to-one relationship with organizations
    organization = models.ForeignKey(Organization, CASCADE)

    # many-to-many relationship with users
    users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return f"{OrganizationRoleLevel(self.name).label} of {self.organization}"


class TeamRole(AuthorizedModel):
    # Role name, selected from role choices
    name = models.CharField(max_length=256, choices=TeamRoleLevel.choices)

    # many-to-one relationship with teams
    team = models.ForeignKey(Team, CASCADE)

    # many-to-many relationship with users
    users = models.ManyToManyField(User, blank=True)
