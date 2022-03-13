from django import forms
from django.utils.translation import gettext_lazy as _


class SearchForm(forms.Form):
    query = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': _('Name, author, translator, publisher or isbn'),
            'autofocus': 'autofocus'
        })
    )


class ClientSearchForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client_query'].required = False

    client_query = forms.CharField(
        label=_('Client'),
        widget=forms.TextInput(attrs={'placeholder': _('Name or phonenumber')})
    )


class CLientSearchStaffForm(forms.Form):
    query = forms.CharField(label='',
        widget=forms.TextInput(attrs={'placeholder': _('Name or phonenumber')})
    )

class BookIsbnSearchForm(forms.Form):
    isbn_query = forms.IntegerField(
        label='ISBN',
        widget=forms.TextInput(attrs={'placeholder': _('ISBN'), 'autofocus': 'autofocus'})
    )



class OrderSearchForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['order_query'].required = False

    order_query = forms.CharField(
        label=_('Order search'),
        widget=forms.TextInput(attrs={'placeholder': _('Client, order or order notes')})
    )
