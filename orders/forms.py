from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Order


class OrderCreateForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = [
            'client', 'client_phone', 'user_email',
            'shipping_method',
        ]


class OrderAdminCheckoutForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer_note'].widget.attrs.update(style='max-height: 4em')

    class Meta:
        model = Order
        fields = [
            'discount', 'channel', 'is_gift', 'paid', 'customer_note',
        ]
        labels ={
            'customer_note': _('Notes'),
            'is_gift': _('Is a gift'),
            'channel': _('Cahnnel'),
        }
