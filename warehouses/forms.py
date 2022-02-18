from django import forms
from phonenumber_field.formfields import PhoneNumberField

from .models import Refund


class RefundClientForm(forms.ModelForm):
    order_id = forms.IntegerField()
    product_isbn = forms.CharField(max_length=13)
    client_phone = PhoneNumberField()

    class Meta:
        model = Refund
        fields = [
            'price', 'discount', 'quantity',
        ]
    field_order = [
        'order_id', 'product_isbn', 'client_phone',
        'price', 'discount', 'quantity',
    ]
