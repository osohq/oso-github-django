from django.forms import Form, CharField, ChoiceField
from .models import RepositoryRoleLevel

# Create the form class.
class RepositoryRoleForm(Form):
    name = CharField(max_length=256, disabled=True)
    role = ChoiceField(choices=RepositoryRoleLevel.choices)
