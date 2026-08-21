from django.shortcuts import redirect
from django.http import HttpResponse
from .google_auth import get_flow


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
    state = request.session.get("state")
    code_verifier = request.session.get("code_verifier")

    flow = get_flow()
    flow.code_verifier = code_verifier
    flow.fetch_token(authorization_response=request.build_absolute_uri())

    credentials = flow.credentials
    request.session["credentials"] = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }

    return HttpResponse("Autenticado con Gmail correctamente. Ya puedes cerrar esta pestaña o volver a la app.")