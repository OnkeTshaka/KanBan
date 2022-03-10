from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from .forms import CustomUserCreationForm, ProfileForm, UserForm
from .models import *

# Create your views here.
def profile(request):
    return render(request, "accounts/profile.html")


def loginPage(request):
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Little Hack to work around re-building the usermodel
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
        except:
            messages.error(request, "User with this email does not exists")
            return redirect("login")

        if user is not None:
            login(request, user)
            return redirect("/")
        else:
            messages.error(request, "Email OR password is incorrect")

    context = {}
    return render(request, "accounts/login.html", context)


def registerPage(request):
    form = CustomUserCreationForm()
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            messages.success(request, "Account successfuly created!")

            user = authenticate(
                request, username=user.username, password=request.POST["password1"]
            )

            if user is not None:
                login(request, user)

            next_url = request.GET.get("next")
            if next_url == "" or next_url == None:
                next_url = "/"
            return redirect(next_url)
        else:
            messages.error(request, "An error has occured with registration")
    context = {"form": form}
    return render(request, "accounts/register.html", context)


def logoutUser(request):
    logout(request)
    return redirect("/")


@login_required(login_url="/")
def userAccount(request):
    profile = request.user.profile

    context = {"profile": profile}
    return render(request, "accounts/account.html", context)


@login_required(login_url="/")
def updateProfile(request):
    user = request.user
    profile = user.profile
    form = ProfileForm(instance=profile)
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=user)
        if user_form.is_valid():
            user_form.save()

        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("account")

    context = {"form": form}
    return render(request, "accounts/profile_form.html", context)
