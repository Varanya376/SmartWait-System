from django.urls import path
from .views import register, login_view, logout_view, forgot_password

urlpatterns = [
    path("register/", register),
    path("login/", login_view),
    path("logout/", logout_view),
    path("forgot/", forgot_password),
]