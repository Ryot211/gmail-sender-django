from django.shortcuts import redirect,render
from django.http import HttpResponse
from googleapiclient.discovery import build
from .google_auth import get_flow
from .models import GoogleCredential
from .forms import EnvioMasivoForm
from .models import EmailEnviado
from .tasks import enviar_email



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



def enviar_view(request):
    if request.method == "POST":
        form = EnvioMasivoForm(request.POST)
        if form.is_valid():
            destinatarios_raw = form.cleaned_data["destinatarios"]
            asunto = form.cleaned_data["asunto"]
            cuerpo = form.cleaned_data["cuerpo"]

            destinatarios = [d.strip() for d in destinatarios_raw.split(",") if d.strip()]

            for destinatario in destinatarios:
                registro = EmailEnviado.objects.create(
                    destinatario=destinatario,
                    asunto=asunto,
                    cuerpo=cuerpo,
                )
                enviar_email.delay(registro.id)

            return render(request, "emails/enviado.html", {"cantidad": len(destinatarios)})
    else:
        form = EnvioMasivoForm()

    return render(request, "emails/enviar.html", {"form": form})

def historial_view(request):
    envios = EmailEnviado.objects.all()
    return render(request, "emails/historial.html", {"envios": envios})