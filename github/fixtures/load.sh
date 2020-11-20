#!/bin/bash

python manage.py loaddata github/fixtures/organizations.json
python manage.py loaddata github/fixtures/users.json
python manage.py loaddata github/fixtures/repos.json
python manage.py loaddata github/fixtures/teams.json
python manage.py loaddata github/fixtures/org_roles.json
python manage.py loaddata github/fixtures/repo_roles.json