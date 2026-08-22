import base64
from email.mime.text import MIMEText

from celery import shared_task
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from .models import EmailEnviado, GoogleCredential


def _get_gmail_service():
    """Reconstruye las credenciales guardadas y arma el cliente de Gmail API."""
    cred_obj = GoogleCredential.objects.first()
    if not cred_obj:
        raise Exception("No hay credenciales de Google guardadas. Inicia sesión en /login/ primero.")

    credentials = Credentials(
        token=cred_obj.token,
        refresh_token=cred_obj.refresh_token,
        token_uri=cred_obj.token_uri,
        client_id=cred_obj.client_id,
        client_secret=cred_obj.client_secret,
        scopes=cred_obj.scopes.split(","),
    )

    # Si el token expiró, lo refrescamos automáticamente y guardamos el nuevo
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        cred_obj.token = credentials.token
        cred_obj.save()

    return build("gmail", "v1", credentials=credentials)


@shared_task
def enviar_email(email_id):
    try:
        registro = EmailEnviado.objects.get(id=email_id)
    except EmailEnviado.DoesNotExist:
        return

    try:
        service = _get_gmail_service()

        message = MIMEText(registro.cuerpo)
        message["to"] = registro.destinatario
        message["subject"] = registro.asunto

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        service.users().messages().send(
            userId="me",
            body={"raw": raw_message},
        ).execute()

        registro.estado = EmailEnviado.Estado.ENVIADO
        registro.error_mensaje = None
        registro.save()

    except Exception as e:
        registro.estado = EmailEnviado.Estado.FALLIDO
        registro.error_mensaje = str(e)
        registro.save()