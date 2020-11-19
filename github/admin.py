from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from github.models import (
    User,
    Repository,
    Organization,
    Team,
    Issue,
    RepositoryRole,
    OrganizationRole,
)

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Repository)
admin.site.register(Organization)
admin.site.register(Team)
admin.site.register(Issue)
admin.site.register(RepositoryRole)
admin.site.register(OrganizationRole)