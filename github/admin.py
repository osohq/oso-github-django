from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from github.models import User, Repository, Organization, Team, Issue

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Repository)
admin.site.register(Organization)
admin.site.register(Team)
admin.site.register(Issue)