# pos/forms.py
from django import forms
from .models import Category, Product

class CheckoutForm(forms.Form):
    payment_method = forms.ChoiceField(choices=[("cash","Efectivo"),("card","Tarjeta")], widget=forms.RadioSelect)
    cash_given = forms.DecimalField(required=False, min_value=0, decimal_places=2, max_digits=12)

class FilterForm(forms.Form):
    METHOD_CHOICES = [("all","Todos"),("cash","Efectivo"),("card","Tarjeta")]
    method = forms.ChoiceField(choices=METHOD_CHOICES, required=False)
    month = forms.IntegerField(required=False, min_value=1, max_value=12)
    year = forms.IntegerField(required=False, min_value=2000, max_value=2100)

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name", "active")

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ("category", "name", "price", "active", "stock")
