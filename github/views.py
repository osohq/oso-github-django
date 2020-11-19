from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import View
from django.utils.timezone import localtime, now
from datetime import datetime, timedelta

from github.models import User, Repository, Issue, Organization, Team

DANGER = 50

# Create your views here.
def index(request):
    return redirect("orgs_index")


@login_required
def orgs_index(request):
    if request.method == "GET":
        context = {"org_list": Organization.objects.all()}
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


@login_required
def repos_index(request, org_name):
    if request.method == "GET":
        repos = Repository.objects.filter(organization__name=org_name)
        context = {"org_name": org_name, "repo_list": repos}
        return render(request, "repos/index.html", context)
    if request.method == "POST":
        try:
            name = request.POST["name"]
        except KeyError as e:
            messages.add_message(request, DANGER, "Missing field: %s" % str(e))
            return render(request, "repos/new.html")
        else:
            if Repository.objects.filter(name=name).count() > 0:
                messages.add_message(
                    request, DANGER, "Repository already exists: %s" % name
                )
                return render(request, "repos/new.html")
            Repository(name=name).save()
            messages.success(request, 'Repository "%s" created successfully' % name)
            return redirect("/repos/")


@login_required
def teams_index(request, org_name):
    if request.method == "GET":
        teams = Team.objects.filter(organization__name=org_name)
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
    context = {"team": team, "members": team.users.all()}
    return render(request, "teams/show.html", context)


def repos_show(request, org_name, repo_name):
    repo = get_object_or_404(Repository, organization__name=org_name, name=repo_name)
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
