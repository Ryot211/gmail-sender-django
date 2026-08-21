from django.db import models


class EmailEnviado(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        ENVIADO = "enviado", "Enviado"
        FALLIDO = "fallido", "Fallido"

    destinatario = models.EmailField()
    asunto = models.CharField(max_length=255)
    cuerpo = models.TextField()
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )
    error_mensaje = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.destinatario} — {self.asunto} ({self.estado})"

    class Meta:
        ordering = ["-creado_en"]