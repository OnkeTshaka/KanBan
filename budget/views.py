import hmac
from hashlib import sha1
from django.shortcuts import render, redirect
from django.conf import settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.decorators import login_required

from .authentication import secure
from .celery import create_todo, delete_todo, sync_todo
from .models import Board, Project
from .forms import BoardForm, ProjectForm

# boards
# index
@login_required(login_url="home")
def boards(request):
    boards = Board.objects.all()
    context = {"boards": boards}
    return render(request, "budget/boards.html", context)


# detail
@login_required(login_url="home")
def board(request, pk):
    board = Board.objects.get(id=pk)
    context = {"board": board}
    return render(request, "budget/board.html", context)


# create
@login_required(login_url="home")
def createBoard(request):
    form = BoardForm()

    if request.method == "POST":
        form = BoardForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        return redirect("/")

    context = {"form": form}
    return render(request, "budget/board_form.html", context)


# edit
@login_required(login_url="home")
def updateBoard(request, pk):
    board = Board.objects.get(id=pk)
    form = BoardForm(instance=board)

    if request.method == "POST":
        form = BoardForm(request.POST, request.FILES, instance=board)
        if form.is_valid():
            form.save()
        return redirect("boards")

    context = {"form": form}
    return render(request, "budget/board_form.html", context)


# delete
@login_required(login_url="home")
def deleteBoard(request, pk):
    board = Board.objects.get(id=pk)

    if request.method == "POST":
        board.delete()
        return redirect("boards")
    context = {"item": board}
    return render(request, "budget/delete.html", context)


# Projects
# index
@login_required(login_url="home")
def projects(request):
    projects = Project.objects.all()
    context = {"projects": projects}
    return render(request, "budget/projects.html", context)


# detail
@login_required(login_url="home")
def project(request, pk):
    project = Project.objects.get(id=pk)
    context = {"project": project}
    return render(request, "budget/project.html", context)


# create
@login_required(login_url="home")
def createProject(request):
    form = ProjectForm()

    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        return redirect("project")

    context = {"form": form}
    return render(request, "budget/project_form.html", context)


# edit
@login_required(login_url="home")
def updateProject(request, pk):
    project = Project.objects.get(id=pk)
    form = ProjectForm(instance=project)

    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
        return redirect("boards")

    context = {"form": form}
    return render(request, "budget/project_form.html", context)


# delete
@login_required(login_url="home")
def deleteProject(request, pk):
    project = Project.objects.get(id=pk)

    if request.method == "POST":
        project.delete()
        return redirect("projects")
    context = {"item": project}
    return render(request, "budget/delete.html", context)


@secure
class HomeView(TemplateView):
    template_name = "budget/override_home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context["boards"] = Board.objects.all()
        return context


@secure
class BoardDetail(DetailView):
    model = Board
    context_object_name = "board"
    template_name = "budget/override_board.html"

    def get_context_data(self, **kwargs):
        context = super(BoardDetail, self).get_context_data(**kwargs)
        context["token"] = getattr(settings, "BUDGET_SECRET_TOKEN")
        context["root"] = reverse("budget-boards")
        return context


class GithubWebhook(APIView):
    permission_classes = (AllowAny,)

    def verify_request(self, request):
        """
        Verify request is from Github using secret token.
        """
        SECRET = getattr(settings, "BUDGET_SECRET_TOKEN", None)
        if not SECRET:
            return True
        header_signature = request.META.get("HTTP_X_HUB_SIGNATURE")
        if not header_signature:
            return False
        sha_name, signature = header_signature.split("=")
        if sha_name != "sha1":
            return False
        mac = hmac.new(
            force_bytes(SECRET), msg=force_bytes(request.body), digestmod=sha1
        )
        if not hmac.compare_digest(
            force_bytes(mac.hexdigest()), force_bytes(signature)
        ):
            return False
        return True

    def post(self, request, *args, **kwargs):
        """
        Respond to incoming github webhook for issue events.
        """

        if not self.verify_request(request):
            return Response(status=status.HTTP_403_FORBIDDEN)

        payload = request.data

        if not payload.get("issue", None):
            return Response(status=status.HTTP_200_OK)

        repo_url = payload.get("repository").get("html_url")
        issue_url = payload.get("issue").get("html_url")
        title = payload.get("issue").get("title")

        action = payload.get("action")
        if action == "opened" or action == "reopened":
            create_todo.delay(repo_url, issue_url, title)
        elif action == "closed":
            delete_todo.delay(issue_url)
        elif action == "edited":
            sync_todo.delay(issue_url, title)

        return Response(status=status.HTTP_200_OK)
