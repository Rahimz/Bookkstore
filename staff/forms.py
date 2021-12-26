from django import forms
from products.models import Product, Good, Category


class ProductCreateForm(forms.ModelForm):

    class Meta:
        model = Product
        exclude = ['import_session', ]
