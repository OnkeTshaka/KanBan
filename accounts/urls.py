from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    # User Authentication
    path("login/", views.loginPage, name="login"),
    path("register/", views.registerPage, name="register"),
    path("logout/", views.logoutUser, name="logout"),
    path("account/", views.userAccount, name="account"),
    path("update_profile/", views.updateProfile, name="update_profile"),
]
