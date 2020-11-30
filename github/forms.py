from django.forms import Form, CharField, ChoiceField
from django.db.models import Q
from .models import RepositoryRole, User, Repository, RepositoryRoleLevel

# Create the form class.
class RepositoryRoleForm(Form):
    username = CharField(max_length=256, disabled=True)
    role = ChoiceField(choices=RepositoryRoleLevel.choices)