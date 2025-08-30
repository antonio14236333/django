# core/urls.py
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path("", lambda r: redirect("pos:sell"), name="home"),
    path("pos/", include("pos.urls")),

    # Auth
    path("accounts/login/", LoginView.as_view(template_name="auth/login.html"), name="login"),
    # Logout por POST (más seguro). Redirige a /pos/sell/ tras salir
    path("accounts/logout/", LogoutView.as_view(next_page="pos:sell"), name="logout"),
]
