from django.contrib import admin
from .models import EmailEnviado, GoogleCredential


@admin.register(EmailEnviado)
class EmailEnviadoAdmin(admin.ModelAdmin):
    list_display = ("destinatario", "asunto", "estado", "creado_en")
    list_filter = ("estado",)
    search_fields = ("destinatario", "asunto")
    readonly_fields = ("creado_en", "actualizado_en")


@admin.register(GoogleCredential)
class GoogleCredentialAdmin(admin.ModelAdmin):
    list_display = ("email", "creado_en", "actualizado_en")
    readonly_fields = ("creado_en", "actualizado_en")    