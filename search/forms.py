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
        self.fields['query'].required = False

    query = forms.CharField(label='Phone',
        widget=forms.TextInput(attrs={'placeholder': _('+989123456789')})
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
