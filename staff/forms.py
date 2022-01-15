from django import forms
from products.models import Product, Good, Category
from orders.models import Order, OrderLine


class ProductCreateForm(forms.ModelForm):

    class Meta:
        model = Product
        exclude = ['import_session', ]


class OrderCreateForm(forms.ModelForm):

    class Meta:
        model = Order
        exclude = ['user', 'token', 'checkout_token' ]

class InvoiceAddForm(forms.ModelForm):

    class Meta:
        model = OrderLine
        fields = ['quantity', 'discount']
