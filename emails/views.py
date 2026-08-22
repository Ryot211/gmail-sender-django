from django.shortcuts import redirect
from django.http import HttpResponse
from googleapiclient.discovery import build
from .google_auth import get_flow
from .models import GoogleCredential


def login_view(request):
    flow = get_flow()
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    request.session["state"] = state
    request.session["code_verifier"] = flow.code_verifier
    return redirect(authorization_url)


def oauth2callback_view(request):
    code_verifier = request.session.get("code_verifier")

    flow = get_flow()
    flow.code_verifier = code_verifier
    flow.fetch_token(authorization_response=request.build_absolute_uri())

    credentials = flow.credentials

    # Obtenemos el email del usuario autenticado
    oauth2_service = build("oauth2", "v2", credentials=credentials)
    user_info = oauth2_service.userinfo().get().execute()
    email = user_info["email"]

    # Guardamos (o actualizamos) las credenciales en la base de datos
    GoogleCredential.objects.update_or_create(
        email=email,
        defaults={
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": ",".join(credentials.scopes),
        },
    )

    return HttpResponse(f"Autenticado como {email}. Credenciales guardadas correctamente.")
