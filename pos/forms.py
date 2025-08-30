from django import forms

class CategoryForm(forms.Form):
    name = forms.CharField(label='Nombre', max_length=100)
    active = forms.BooleanField(label='Activo', required=False, initial=True)

class ProductForm(forms.Form):
    name = forms.CharField(label='Nombre', max_length=100)
    price = forms.DecimalField(label='Precio', max_digits=10, decimal_places=2)
    category_id = forms.ChoiceField(label='Categoría')
    active = forms.BooleanField(label='Activo', required=False, initial=True)

    def __init__(self, *args, **kwargs):
        categories = kwargs.pop('categories', [])
        super().__init__(*args, **kwargs)
        self.fields['category_id'].choices = [
            (c.id, c.name) for c in categories
        ]
