from django.urls import path
from django.contrib.auth import views as auth_views

from .views import index, repos_index


urlpatterns = [
    path("", index, name="index"),
    path("repos/", repos_index, name="repos_index"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]