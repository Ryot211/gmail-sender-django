from django import forms


class EnvioMasivoForm(forms.Form):
    destinatarios = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4, "placeholder": "uno@ejemplo.com, otro@ejemplo.com"}),
        help_text="Separa los correos con comas.",
    )
    asunto = forms.CharField(max_length=255)
    cuerpo = forms.CharField(widget=forms.Textarea(attrs={"rows": 6}))