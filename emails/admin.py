from django.contrib import admin
from .models import EmailEnviado


@admin.register(EmailEnviado)
class EmailEnviadoAdmin(admin.ModelAdmin):
    list_display = ("destinatario", "asunto", "estado", "creado_en")
    list_filter = ("estado",)
    search_fields = ("destinatario", "asunto")
    readonly_fields = ("creado_en", "actualizado_en")