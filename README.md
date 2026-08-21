# Gmail Sender — Django + Celery

Aplicación web para el envío de correos (individuales y masivos) integrando la API de Gmail, con procesamiento asíncrono mediante Celery y un historial de envíos persistido en PostgreSQL.

> 🚧 **Estado:** en desarrollo activo.

## Stack

- **Backend:** Django
- **Cola de tareas:** Celery + Redis
- **Base de datos:** PostgreSQL
- **Autenticación / envío:** Gmail API (OAuth2)
- **Infraestructura local:** Docker Compose (PostgreSQL + Redis)

## Cómo funciona

1. El usuario se autentica con su cuenta de Gmail vía OAuth2.
2. Desde un formulario, sube uno o varios destinatarios junto con asunto y mensaje.
3. Por cada destinatario se crea un registro en la base de datos con estado `pendiente`, y se encola una tarea de Celery.
4. Celery procesa cada tarea en segundo plano, llamando a la Gmail API para enviar el correo.
5. Cada tarea actualiza su registro a `enviado` o `fallido` según el resultado.
6. El usuario puede consultar el historial completo de envíos, con su estado.

## Requisitos previos

- Python 3.11+
- Docker y Docker Compose
- Una cuenta de Google con un proyecto en Google Cloud Console (para las credenciales de la Gmail API)

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

   Crea un archivo `.env` en la raíz del proyecto (usa `.env.example` como referencia):

   ```
   DB_NAME=gmail_sender
   DB_USER=gmail_sender_user
   DB_PASSWORD=changeme123
   DB_HOST=localhost
   DB_PORT=5433
   SECRET_KEY=tu-clave-secreta-aqui
   ```

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
   celery -A config worker -l info
   ```

## Estructura del proyecto

```
gmail-sender-django/
├── config/              # Configuración principal de Django
├── docker-compose.yml   # Servicios de PostgreSQL y Redis
├── requirements.txt     # Dependencias de Python
├── manage.py
└── .env                 # Variables de entorno (no versionado)
```

## Roadmap

- [x] Setup del proyecto y entorno de desarrollo
- [x] Conexión con PostgreSQL vía Docker
- [ ] Configuración de credenciales OAuth2 con Gmail API
- [ ] Modelo de datos para registros de envío
- [ ] Autenticación de usuarios con Gmail
- [ ] Configuración de Celery y tareas de envío
- [ ] Formulario de envío masivo
- [ ] Vista de historial de envíos
- [ ] Manejo de errores y reintentos
- [ ] Despliegue en producción

## Autor

**Bryan Gallardo**
Desarrollador de software — Latacunga, Ecuador
[GitHub](https://github.com/Ryot211) · [LinkedIn](https://www.linkedin.com/in/bryan-gallardo-813640176)