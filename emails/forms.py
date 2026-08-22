from django import forms


class EnvioMasivoForm(forms.Form):
    destinatarios = forms.CharField(
        widget=forms.Textarea(attrs={
            "rows": 3,
            "placeholder": "uno@ejemplo.com, otro@ejemplo.com",
            "class": "w-full rounded-md bg-stone-950 border border-stone-700 px-3 py-2 text-sm text-stone-200 placeholder-stone-600 focus:outline-none focus:ring-2 focus:ring-amber-600 focus:border-amber-600",
        }),
        help_text="Separa los correos con comas.",
    )
    asunto = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            "class": "w-full rounded-md bg-stone-950 border border-stone-700 px-3 py-2 text-sm text-stone-200 placeholder-stone-600 focus:outline-none focus:ring-2 focus:ring-amber-600 focus:border-amber-600",
        }),
    )
    cuerpo = forms.CharField(
        widget=forms.Textarea(attrs={
            "rows": 6,
            "class": "w-full rounded-md bg-stone-950 border border-stone-700 px-3 py-2 text-sm text-stone-200 placeholder-stone-600 focus:outline-none focus:ring-2 focus:ring-amber-600 focus:border-amber-600",
        }),
    )