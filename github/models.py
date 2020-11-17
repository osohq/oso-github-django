from django.db import models

# Create your models here.
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db.models.deletion import CASCADE
from django_oso.models import AuthorizedModel


class User(AbstractUser):
    # basic info
    email = models.CharField(max_length=256)
    organizations = models.ManyToManyField("Organization")


class Organization(AuthorizedModel):
    name = models.CharField(max_length=1024)
    members = models.ManyToManyField(User, through="OrganizationMember")


class Repository(AuthorizedModel):
    # basic information
    amount = models.IntegerField()
    description = models.CharField(max_length=1024)

    # ownership/category
    owner = models.ForeignKey("User", CASCADE)
    organization = models.ForeignKey("Organization", CASCADE)

    # time info
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
