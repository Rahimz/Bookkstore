from django import forms
from django.utils.translation import gettext_lazy as _

from products.models import Product, Good, Category, Craft, Image
from orders.models import Order, OrderLine


class ProductCreateForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = [
            'name', 'isbn', 'collection_name', 'number_in_collection', 'category', 'author', 'translator',
            'illustrator', 'latin_name', 'author_latin_name',
            # 'image', 'image_alt',
            'description', 'age_range', 'product_type', 'weight',
            'size', 'cover_type', 'page_number', 'publisher', 'publisher_2', 'publish_year',
            'edition',
            # 'price', 'stock',
            # 'has_other_prices',
            # 'price_1', 'stock_1', 'price_2', 'stock_2', 'price_3', 'stock_3', 'price_4', 'stock_4', 'price_5', 'stock_5',
            # 'price_used', 'stock_used',
            'store_positon', 'admin_note',
            # 'available', 'available_in_store', 'available_online',
        ]
        labels = {
            'name':_('Name'), 'isbn': _('ISBN'), 'collection_name': _('Collection name'), 'number_in_collection': _('Number in collection'),
            'category': _('Category'), 'author': _('Author'), 'translator': _('Translator'),
            'illustrator': _('Illustrator'), 'latin_name': _('Latin name'), 'author_latin_name': _('Author latin name'),

            'description': _('Description'), 'age_range': _('Age range'), 'product_type': _('Product type'), 'weight': _('Weight'),
            'size': _('Size'), 'cover_type': _('Cover type'), 'page_number': _('Page number'), 'publisher': _('Publisher'), 'publisher_2': _('Publisher 2'),
            'publish_year': _('Publish year'), 'edition': _('Edition'),

            'store_positon': _('Store position'), 'admin_note': _('Admin note'),
        }

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
        self.fields['quantity'].widget.attrs.update(style='max-width: 2em')
        self.fields['discount'].widget.attrs.update(style='max-width: 4em')

    remove = forms.BooleanField(required=False)

    class Meta:
        model = OrderLine
        fields = ('quantity', 'discount',)
        labels = {
            'quantity': _('Quantity')
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
        fields = ['shipped_code', 'shipping_status', 'shipping_time', 'is_packaged']
        labels = {
            'shipped_code': _('Shipping code'),
            'shipping_status': _('Shipping status'),
            'shipping_time': _('Shipping time'),
            'is_packaged': _('Is packaged')
        }
        widgets = {
            'shipped_code': forms.TextInput(attrs={'autofocus': 'autofocus'})
        }


class ProductCollectionForm(forms.Form):
    collection_field = forms.CharField(
        label=_('Related product'),
        max_length=13,
        widget=forms.TextInput(attrs={'placeholder': _('Please add one ISBN each time')})
    )
    # class Meta:
    #     model = Product
    #     fields = ['collection_set',]
    #     labels = {
    #         'collection_set': _('Enter just one ISBN each time')
    #     }
    #     widgets = {
    #         'collection_set': forms.TextInput(attrs={'placeholder': _('Just enter each ISBN in a new line')})
    #     }


class AdminPriceManagementForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = [
            'price_used',
            ]
        labels ={
            'price_used': _('Price used'),
        }


class AdminPriceStockManagementForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'price', 'stock', 'price_used', 'stock_used',
            ]
        labels ={
            'price': _('Main price'),
            'stock': _('Main stock'),
            'price_used': _('Used price'),
            'stock_used': _('Used stock'),
        }
        help_texts ={
            'price': _('Only the biggest price'),
            'stock': _('If it\'s bigger than the stock a purchase will create for it'),
            'price_used': _('As same as Bahman key'),
            'stock_used': _('Just for editing the databse for books that is in store but not in database'),
        }


class OnlineAdminPriceStockManagementForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'price',
            # 'stock', 'price_used', 'stock_used',
            ]
        labels ={
            'price': _('Main price'),
            # 'stock': _('Main stock'),
            # 'price_used': _('Used price'),
            # 'stock_used': _('Used stock'),
        }
        help_texts ={
            'price': _('Only the biggest price'),
            # 'stock': _('If it\'s bigger than the stock a purchase will create for it'),
            # 'price_used': _('As same as Bahman key'),
            # 'stock_used': _('Just for editing the databse for books that is in store but not in database'),
        }


class CraftUpdateForm(forms.ModelForm):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['slug'].required = False

    class Meta:
        model = Product
        fields = [
            'name', 'craft_category', 'barcode_number', 'stock', 'price', 'description', 'available']


class ProductImageManagementForm(forms.ModelForm):

    class Meta:
        model = Image
        fields = ['file', 'image_alt', 'variation']
        widgets = {
            'image_alt': forms.TextInput(attrs={'placeholder': _('Image alt is a description for defining the image')})
        }
