from django import forms

from .models import Payment


class PaymentForm(forms.ModelForm):

    class Meta:
        model = Payment
        fields = [
            'client_name' , 'client_phone', 'amount', 
        ]
