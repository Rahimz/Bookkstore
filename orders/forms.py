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
            'discount': _('Invoice discount'),
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
        labels = {
            'vendor': _('Vendor'),
            'deadline_days': _('Payment deadline'),
        }

class PurchaseLineAddForm(forms.ModelForm):

    class Meta:
        model = PurchaseLine
        exclude = ['vendor']


class PriceAddForm(forms.Form):
    STATUS_CHOICES = (
        ('new', _('New')),
        ('used', _('Used')),
    )
    variation = forms.ChoiceField(choices = STATUS_CHOICES)
    price = forms.DecimalField(max_digits=10, decimal_places=0)
    # quantity = forms.IntegerField()


class PurchaseLineUpdateForm(forms.ModelForm):
    class Meta:
        model = PurchaseLine
        fields = [
            'quantity', 'discount_percent', 'discount',
        ]
        labels = {
            'price': _('Purchase price'),

        }
