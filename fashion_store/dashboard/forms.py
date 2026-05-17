from django import forms

from fashion_store.products.models import Product
from fashion_store.products.models import ProductVariant


class DashboardProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "category",
            "name",
            "description",
            "price",
            "compare_price",
            "image",
            "has_variants",
            "is_active",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "price": forms.NumberInput(attrs={"min": 0}),
            "compare_price": forms.NumberInput(attrs={"min": 0}),
        }

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price and price < 0:
            msg = "El precio no puede ser negativo"
            raise forms.ValidationError(msg)
        return price

    def clean_compare_price(self):
        price = self.cleaned_data.get("price")
        compare = self.cleaned_data.get("compare_price")
        if compare and price and compare <= price:
            msg = "El precio de comparación debe ser mayor al precio normal"
            raise forms.ValidationError(msg)
        return compare


class VariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = [
            "size",
            "color",
            "color_code",
            "stock",
            "price_override",
            "sku",
            "is_active",
        ]
        widgets = {
            "color_code": forms.TextInput(
                attrs={"type": "color", "class": "form-control-color"},
            ),
            "price_override": forms.NumberInput(attrs={"min": 0}),
            "stock": forms.NumberInput(attrs={"min": 0}),
        }


VariantFormSet = forms.inlineformset_factory(
    Product,
    ProductVariant,
    form=VariantForm,
    extra=1,
    can_delete=True,
)

DashboardVariantFormSet = VariantFormSet
