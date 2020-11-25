from django.urls import path
from django.contrib.auth import views as auth_views

from .views import (
    index,
    repos_index,
    repos_show,
    issues_index,
    orgs_index,
    teams_index,
    teams_show,
    org_people_index,
    repos_new,
    repo_roles_index,
)


urlpatterns = [
    path("", index, name="index"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("orgs/", orgs_index, name="orgs_index"),
    path("orgs/<org_name>/repos/", repos_index, name="repos_index"),
    path("orgs/<org_name>/repos/new/", repos_new, name="repos_new"),
    path("orgs/<org_name>/repos/<repo_name>", repos_show, name="repos_show"),
    path(
        "orgs/<org_name>/repos/<repo_name>/issues/", issues_index, name="issues_index"
    ),
    path(
        "orgs/<org_name>/repos/<repo_name>/roles/",
        repo_roles_index,
        name="repo_roles_index",
    ),
    path("orgs/<org_name>/teams/", teams_index, name="teams_index"),
    path("orgs/<org_name>/teams/<team_name>", teams_show, name="teams_show"),
    path("orgs/<org_name>/people/", org_people_index, name="org_people_index"),
]