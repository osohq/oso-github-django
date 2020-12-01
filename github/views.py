from django.db.models import F
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import View
from django.utils.timezone import localtime, now
from django.http import HttpRequest
from datetime import datetime, timedelta

from django_oso.auth import authorize, authorize_model
from django_oso.decorators import authorize_request
from django_oso import Oso

from github.models import (
    User,
    Repository,
    Issue,
    Organization,
    Team,
    RepositoryRole,
    OrganizationRole,
    RepositoryRoleLevel,
)
from github.forms import RepositoryRoleForm

DANGER = 50

# Create your views here.
def index(request):
    return redirect("orgs_index")


# ORGANIZATION VIEWS


@login_required
def orgs_index(request):
    if request.method == "GET":
        org_filter = authorize_model(request, Organization, action="read")
        orgs = Organization.objects.filter(org_filter)
        context = {"org_list": orgs}
        return render(request, "orgs/index.html", context)
    # if request.method == "POST":
    #     if "delete_mapping" in request.POST:
    #         RoleMappings.objects.get(id=request.POST["delete_mapping"]).delete()
    #     elif "create_mapping" in request.POST:
    #         form = request.POST
    #         RoleMappings(
    #             organization=org, gsuite_group=form["gsuite_group"], role=form["role"]
    #         ).save()
    #     else:
    #         logger.warn(request.POST)
    # return render(request, "orgs/show.html", {"org": org})


@authorize_request
def org_people_index(request, org_name):
    if request.method == "GET":
        roles = OrganizationRole.objects.filter(
            organization__name=org_name
        ).prefetch_related("users")
        user_roles = []
        for role in roles:
            for user in role.users.all():
                user_roles.append((user.username, role.name))

        return render(
            request,
            "orgs/people.html",
            context={"org_name": org_name, "user_roles": user_roles},
        )


# REPOSITORY VIEWS


@login_required
@authorize_request
def repos_index(request, org_name):
    if request.method == "GET":
        repo_filter = authorize_model(request, Repository, action="read")
        repos = Repository.objects.filter(repo_filter, organization__name=org_name)
        context = {"org_name": org_name, "repo_list": repos}
        return render(request, "repos/index.html", context)
    if request.method == "POST":
        try:
            name = request.POST["name"]
        except KeyError as e:
            messages.add_message(request, DANGER, "Missing field: %s" % str(e))
            return render(request, f"repos/new.html")
        else:
            if Repository.objects.filter(name=name).count() > 0:
                messages.add_message(
                    request, DANGER, "Repository already exists: %s" % name
                )
                return render(request, "repos/new.html", context={"org_name": org_name})

            # create the repository
            repo = Repository(
                name=name, organization=Organization.objects.get(name=org_name)
            )
            repo.save()
            # TODO: need to create the base roles every time a new repo is created
            for (role_level, _) in RepositoryRoleLevel.choices:
                role = RepositoryRole(name=role_level, repository=repo)
                role.save()
                if role.name == RepositoryRoleLevel.ADMIN:
                    role.users.add(request.user)
                    role.save()
            messages.success(request, 'Repository "%s" created successfully' % name)
            print(org_name)
            return redirect(f"/orgs/{org_name}/repos/")


def repos_new(request, org_name):
    return render(request, "repos/new.html", context={"org_name": org_name})


def repos_show(request, org_name, repo_name):
    repo = get_object_or_404(Repository, organization__name=org_name, name=repo_name)
    authorize(request, repo, action="read")
    contributors = len(repo.name)
    commits = contributors * 17
    last_updated = localtime(now()) - timedelta(hours=commits, minutes=contributors)
    return render(
        request,
        "repos/show.html",
        {
            "org_name": org_name,
            "repo": repo,
            "commits": commits,
            "contributors": contributors,
            "last_updated": last_updated,
        },
    )


@authorize_request
def repo_roles_index(request, org_name, repo_name):
    if request.method == "GET":
        roles = RepositoryRole.objects.filter(
            repository__name=repo_name, repository__organization__name=org_name
        ).prefetch_related("users")
        user_forms = []
        team_forms = []
        for role in roles:
            for user in role.users.all():
                form = RepositoryRoleForm(
                    initial={"name": user.username, "role": role.name}
                )
                user_forms.append((user.username, form))
            for team in role.teams.all():
                form = RepositoryRoleForm(
                    initial={"name": team.name, "role": role.name}
                )
                team_forms.append((team.name, form))

        user_forms.sort(key=lambda x: x[0])
        team_forms.sort(key=lambda x: x[0])

        return render(
            request,
            "repos/roles.html",
            context={
                "org_name": org_name,
                "repo_name": repo_name,
                "user_forms": user_forms,
                "team_forms": team_forms,
            },
        )
    elif request.method == "POST":
        form = RepositoryRoleForm(request.POST)
        new_role_name = form["role"].value()
        new_role = RepositoryRole.objects.get(
            repository__name=repo_name, name=new_role_name
        )
        try:
            username = request.POST.get("username")
            user = User.objects.get(username=username)

            # TODO: improve updating roles with library support
            old_role = RepositoryRole.objects.get(
                repository__name=repo_name, users=user
            )
            user.repositoryrole_set.remove(old_role)
            user.repositoryrole_set.add(new_role)
        except:
            teamname = request.POST.get("teamname")
            team = Team.objects.get(name=teamname)

            # TODO: improve updating roles with library support
            old_role = RepositoryRole.objects.get(
                repository__name=repo_name, teams=team
            )
            team.repositoryrole_set.remove(old_role)
            team.repositoryrole_set.add(new_role)

        return redirect(request.path_info)


# TEAM VIEWS


@login_required
@authorize_request
def teams_index(request, org_name):
    if request.method == "GET":
        team_filter = authorize_model(request, Team, action="read")
        teams = Team.objects.filter(team_filter, organization__name=org_name)
        context = {"org_name": org_name, "team_list": teams}
        return render(request, "teams/index.html", context)
    # if request.method == "POST":
    #     try:
    #         name = request.POST["name"]
    #     except KeyError as e:
    #         messages.add_message(request, DANGER, "Missing field: %s" % str(e))
    #         return render(request, "repos/new.html")
    #     else:
    #         if Repository.objects.filter(name=name).count() > 0:
    #             messages.add_message(
    #                 request, DANGER, "Repository already exists: %s" % name
    #             )
    #             return render(request, "repos/new.html")
    #         Repository(name=name).save()
    #         messages.success(request, 'Repository "%s" created successfully' % name)
    #         return redirect("/repos/")


def teams_show(request, org_name, team_name):
    team = get_object_or_404(Team, organization__name=org_name, name=team_name)
    context = {
        "team": team,
        "members": User.objects.filter(teamrole__team=team),
        "roles": RepositoryRole.objects.filter(teams=team),
    }
    return render(request, "teams/show.html", context)


# ISSUE VIEWS


def issues_index(request, org_name, repo_name):
    if request.method == "GET":
        try:
            issues = Issue.objects.filter(
                repository__organization__name=org_name, repository__name=repo_name
            )
            context = {
                "org_name": org_name,
                "repo_name": repo_name,
                "issue_list": issues,
            }
        except:
            context = {"org_name": org_name, "repo_name": repo_name, "issue_list": []}
        return render(request, "issues/index.html", context)
    # if request.method == "POST":
    #     try:
    #         name = request.POST["name"]
    #     except KeyError as e:
    #         messages.add_message(request, DANGER, "Missing field: %s" % str(e))
    #         return render(request, "repos/new.html")
    #     else:
    #         if Repository.objects.filter(name=name).count() > 0:
    #             messages.add_message(
    #                 request, DANGER, "Repository already exists: %s" % name
    #             )
    #             return render(request, "repos/new.html")
    #         Repository(name=name).save()
    #         messages.success(request, 'Repository "%s" created successfully' % name)
    #         return redirect("/repos/")


# CONTEXT PROCESSORS


def org_context_processor(request):
    """Pass authZ context into templates."""
    split_path = request.path.split("/")
    if len(split_path) > 3 and split_path[1] == "orgs":
        org_name = split_path[2]
        people_request = HttpRequest()
        people_request.path = f"/orgs/{org_name}/people/"
        can_view_people = Oso.is_allowed(request.user, "GET", people_request)
        return {"can_view_people": can_view_people}
    return {}