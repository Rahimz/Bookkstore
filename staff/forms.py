from django import forms
from products.models import Product, Good, Category
from orders.models import Order, OrderLine


class ProductCreateForm(forms.ModelForm):

    class Meta:
        model = Product
        exclude = ['import_session', ]


class CategoryCreateForm(forms.ModelForm):

    class Meta:
        model = Category
        exclude = ['slug', ]


class OrderCreateForm(forms.ModelForm):

    class Meta:
        model = Order
        exclude = ['user', 'token', 'checkout_token' ]

class InvoiceAddForm(forms.ModelForm):
    remove = forms.BooleanField(required=False)

    class Meta:
        model = OrderLine
        fields = ('quantity', 'discount',)
        labels = {
            'quantity': 'quantity'
        }
        widgets = {
            'quantity': forms.TextInput(attrs={'placeholder': 'quantity'})
        }
