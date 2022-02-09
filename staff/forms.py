from django import forms
from django.utils.translation import gettext_lazy as _

from products.models import Product, Good, Category
from orders.models import Order, OrderLine


class ProductCreateForm(forms.ModelForm):

    class Meta:
        model = Product
        exclude = ['import_session', 'isbn_9']


class CategoryCreateForm(forms.ModelForm):

    class Meta:
        model = Category
        exclude = ['slug', ]


class OrderCreateForm(forms.ModelForm):

    class Meta:
        model = Order
        exclude = ['user', 'token', 'checkout_token' ]

class InvoiceAddForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['quantity'].widget.attrs.update(style='max-width: 4em')
        self.fields['discount'].widget.attrs.update(style='max-width: 6em')

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


class OrderShippingForm(forms.ModelForm):
    # shipped = forms.BooleanField(label='', required=False)
    # STATUS_CHOICES = (
    #     ('', _('')),
    #     ('fulfilled', _('Fully shipped')),
    #     ('unfulfilled', _('Semi shipped'))
    # )
    # shipping_status = forms.ChoiceField(choices = STATUS_CHOICES, label=_("Shipping status"), initial='fulfilled', widget=forms.Select(), required=True)
    # shipping_status = forms.ChoiceField(choices = STATUS_CHOICES, label=_("Shipping status"), widget=forms.Select(), required=True)

    class Meta:
        model = Order
        fields = ['shipped_code', 'shipping_status']
        widgets = {
            'shipped_code': forms.TextInput(attrs={'autofocus': 'autofocus'})
        }
