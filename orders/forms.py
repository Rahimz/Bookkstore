from django import forms
from .models import Order


class OrderCreateForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = [
            'client', 'client_phone', 'user_email',
            'shipping_method',
        ]


class OrderAdminCheckoutForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = [
            'customer_note', 'paid',
        ]
        labels ={
            'customer_note': 'Notes'
        }
