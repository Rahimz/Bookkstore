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
            'shipping_method', 'shipping_cost', 'shipping_time',
        ]
        labels ={
            'customer_note': _('Notes'),
            'is_gift': _('Is a gift'),
            'channel': _('Cahnnel'),
            'discount': _('Invoice discount'),
            'shipping_method': _('Shipping method'),
            'shipping_cost': _('Shipping cost'),
            'shipping_time': _('Shipping time'),
        }


class OrderPaymentManageForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'pay_receipt', 'paid', 'customer_note', 'shipping_time'
        ]

class PurchaseCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
	    super().__init__(*args, **kwargs)
	    self.fields['vendor'].required = True

    class Meta:
        model = Purchase
        fields = ['vendor', 'deadline_days', 'paper_invoice_number', 'discount', 'discount_percent']
        labels = {
            'vendor': _('Vendor'),
            'deadline_days': _('Payment deadline'),
            'paper_invoice_number': _('Paper invoice number'),
            'discount': _('Invoice overal discount'),
            'discount_percent': _('Overal discount percent'),
        }
        validators = {
            'discount_percent': [MinValueValidator(0), MaxValueValidator(100)]
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
            'quantity', 'discount', 'discount_percent', 
        ]
        labels = {
            'price': _('Purchase price'),

        }
