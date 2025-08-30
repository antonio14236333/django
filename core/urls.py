# core/urls.py
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda r: redirect('pos:sell'), name='home'),
    path('pos/', include('pos.urls')),
    path('accounts/login/', LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('accounts/logout/', LogoutView.as_view(next_page='pos:sell'), name='logout'),
]
