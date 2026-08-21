from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("oauth2callback/", views.oauth2callback_view, name="oauth2callback"),
]