# Gmail Sender — Django + Celery

Aplicación web para el envío de correos (individuales y masivos) integrando la API de Gmail, con procesamiento asíncrono mediante Celery y un historial de envíos persistido en PostgreSQL.

> ✅ **Estado:** flujo completo funcionando en local — autenticación OAuth2, envío masivo con cola en background, historial y reintentos automáticos. Pendiente: despliegue en producción.

## Stack

- **Backend:** Django 6.1
- **Cola de tareas:** Celery + Redis
- **Base de datos:** PostgreSQL 16 (vía Docker Compose)
- **Autenticación / envío:** Gmail API (OAuth2, scope `gmail.send`)
- **Driver de base de datos:** `psycopg` v3 (no `psycopg2` — ver nota en Troubleshooting)
- **Frontend:** Django Templates + Tailwind CSS (CDN) — modo oscuro, paleta cálida (stone + amber)
- **Infraestructura local:** Docker Compose (PostgreSQL + Redis)

## Cómo funciona

1. El usuario se autentica con su cuenta de Gmail vía OAuth2 (`/login/`). Las credenciales quedan guardadas de forma persistente en PostgreSQL (modelo `GoogleCredential`), no solo en la sesión — así el worker de Celery puede usarlas sin depender del navegador.
2. Desde `/enviar/`, sube uno o varios destinatarios (separados por comas), asunto y mensaje.
3. Por cada destinatario se crea un registro `EmailEnviado` con estado `pendiente`, y se encola una tarea de Celery (`enviar_email.delay(...)`).
4. El worker de Celery procesa cada tarea en segundo plano: reconstruye las credenciales OAuth2 (refrescando el token si expiró), arma el correo en formato MIME, y lo envía vía Gmail API.
5. Si el envío falla, la tarea reintenta automáticamente hasta 3 veces (con 30s de espera entre intentos) antes de marcar el registro como `fallido`.
6. En `/historial/` se puede ver el estado de todos los envíos (pendiente / enviado / fallido), con badges de color.

## Requisitos previos

- Python 3.11+
- Docker y Docker Compose
- Un proyecto en Google Cloud Console con la Gmail API habilitada y credenciales OAuth2 (tipo "Aplicación web")

## Instalación local

1. **Clona el repositorio**

   ```bash
   git clone https://github.com/Ryot211/gmail-sender-django.git
   cd gmail-sender-django
   ```

2. **Crea y activa el entorno virtual**

   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   source venv/bin/activate  # macOS/Linux
   ```

3. **Instala las dependencias**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configura las variables de entorno**

   Crea un archivo `.env` en la raíz del proyecto (asegúrate de guardarlo con codificación UTF-8, no UTF-16/ANSI):

   ```
   DB_NAME=gmail_sender
   DB_USER=gmail_sender_user
   DB_PASSWORD=changeme123
   DB_HOST=localhost
   DB_PORT=5433
   SECRET_KEY=tu-clave-secreta-aqui

   GOOGLE_CLIENT_ID=tu-client-id
   GOOGLE_CLIENT_SECRET=tu-client-secret
   GOOGLE_REDIRECT_URI=http://localhost:8000/oauth2callback/

   OAUTHLIB_INSECURE_TRANSPORT=1
   ```

   > ⚠️ `OAUTHLIB_INSECURE_TRANSPORT=1` es **solo para desarrollo local** (permite el intercambio de tokens OAuth2 sobre HTTP). Nunca debe estar activo en producción, donde todo corre sobre HTTPS real.

5. **Levanta PostgreSQL y Redis con Docker**

   ```bash
   docker compose up -d
   ```

6. **Aplica las migraciones**

   ```bash
   python manage.py migrate
   ```

7. **Corre el servidor de desarrollo**

   ```bash
   python manage.py runserver
   ```

8. **Levanta el worker de Celery** (en otra terminal, con el entorno virtual activo)

   ```bash
   celery -A config worker -l info --pool=solo
   ```

   > El flag `--pool=solo` es necesario en Windows, donde el pool por defecto de Celery (`prefork`) no funciona bien.

9. **Prueba el flujo completo**

   - Entra a `http://localhost:8000/login/` (usa siempre `localhost`, no `127.0.0.1` — ver Troubleshooting) y autoriza tu cuenta de Gmail.
   - Ve a `http://localhost:8000/enviar/` y envía un correo de prueba.
   - Revisa `http://localhost:8000/historial/` para ver el estado del envío.

## Estructura del proyecto

```
gmail-sender-django/
├── config/
│   ├── settings.py           # Configuración de Django, PostgreSQL, Celery
│   ├── celery.py              # Inicialización de la app de Celery
│   └── urls.py
├── emails/
│   ├── models.py               # EmailEnviado, GoogleCredential
│   ├── views.py                 # login, oauth2callback, enviar, historial
│   ├── forms.py                  # EnvioMasivoForm
│   ├── tasks.py                   # Tarea enviar_email (Celery)
│   ├── google_auth.py              # Configuración del flujo OAuth2 (Flow)
│   ├── admin.py                     # Registro en el panel de administración
│   ├── urls.py
│   └── templates/emails/
│       ├── base.html                 # Layout compartido (nav, modo oscuro)
│       ├── enviar.html
│       ├── enviado.html
│       └── historial.html
├── docker-compose.yml         # Servicios de PostgreSQL y Redis
├── requirements.txt
├── manage.py
└── .env                        # Variables de entorno (no versionado)
```

## Troubleshooting (problemas reales resueltos durante el desarrollo)

Documentado para referencia propia y de quien revise el repo:

- **`UnicodeDecodeError` al conectar con PostgreSQL en Windows**: bug conocido de `psycopg2` en Windows con configuración regional en español. Solución: usar `psycopg` v3 en vez de `psycopg2-binary` (`pip install "psycopg[binary]"`), Django lo detecta automáticamente.
- **`FATAL: no existe el rol` / `la autenticación password falló`**: causado por otro PostgreSQL nativo de Windows corriendo en el mismo puerto 5432 que el contenedor de Docker. Solución: exponer el contenedor en un puerto distinto (`5433:5432` en `docker-compose.yml`).
- **`InsecureTransportError: OAuth 2 MUST utilize https`**: `oauthlib` bloquea el intercambio de tokens sobre HTTP por defecto. Solución para desarrollo: variable de entorno `OAUTHLIB_INSECURE_TRANSPORT=1` (nunca usar en producción).
- **`InvalidGrantError: Missing code verifier`**: dos causas posibles —
  1. El `Flow` de `login_view` y `oauth2callback_view` deben compartir el mismo `code_verifier` (PKCE) — se guarda en `request.session` durante el login y se recupera en el callback.
  2. `localhost` y `127.0.0.1` son dominios distintos para las cookies del navegador — el flujo completo (login → Google → callback) debe usar siempre el mismo host, coincidiendo con `GOOGLE_REDIRECT_URI`.

## Roadmap

- [x] Setup del proyecto y entorno de desarrollo
- [x] Conexión con PostgreSQL vía Docker
- [x] Configuración de credenciales OAuth2 con Gmail API
- [x] Modelo de datos para registros de envío (`EmailEnviado`)
- [x] Autenticación de usuarios con Gmail (login + callback funcionando)
- [x] Persistir el token OAuth2 en base de datos (`GoogleCredential`)
- [x] Configuración de Celery y tarea de envío (`enviar_email`)
- [x] Formulario de envío masivo
- [x] Vista de historial de envíos
- [x] Diseño con modo oscuro (Tailwind, paleta cálida)
- [x] Reintentos automáticos ante fallos temporales
- [ ] Despliegue en producción (Render/Railway con PostgreSQL, Redis y worker de Celery)

## Autor

**Bryan Gallardo**
Desarrollador de software — Latacunga, Ecuador
[GitHub](https://github.com/Ryot211) · [LinkedIn](https://www.linkedin.com/in/bryan-gallardo-813640176)