from django import forms

from .models import ShippingAddress


class CheckoutForm(forms.ModelForm):
    email = forms.EmailField(required=False, label="Correo electrónico")

    class Meta:
        model = ShippingAddress
        fields = ["full_name", "phone", "address_line", "city", "department", "notes"]
        labels = {
            "full_name": "Nombre completo",
            "phone": "Teléfono",
            "address_line": "Dirección",
            "city": "Ciudad",
            "department": "Departamento",
            "notes": "Notas (opcional)",
        }
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
