from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("oauth2callback/", views.oauth2callback_view, name="oauth2callback"),
    path("enviar/", views.enviar_view, name="enviar"),
    path("historial/", views.historial_view, name="historial"),
]