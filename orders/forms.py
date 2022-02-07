from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from .models import Order, Purchase, PurchaseLine


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


class PurchaseCreateForm(forms.ModelForm):
    # payment_days = forms.IntegerField(
    #     required=False,
    #     label=_('Payment deadline'),
    #     help_text=_('Payment term in days between 1 and 120'),
    #     validators=[MinValueValidator(1), MaxValueValidator(120)],
    # )

    class Meta:
        model = Purchase
        fields = ['vendor', 'deadline_days']

class PurchaseLineAddForm(forms.ModelForm):

    class Meta:
        model = PurchaseLine
        exclude = ['vendor']
