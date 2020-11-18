from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from github.models import User, Repository

DANGER = 50

# Create your views here.
def index(request):
    try:
        user = User.objects.get(name=request.user)
        context = {
            "repo_list": user.repositories.all(),
            "org_list": user.organizations.all(),
        }
    except Exception as e:
        context = {"repo_list": [], "org_list": []}
    return render(request, "index.html", context)


@login_required
def repos_index(request):
    if request.method == "GET":
        repos = Repository.objects.all()
        context = {"repo_list": repos}
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