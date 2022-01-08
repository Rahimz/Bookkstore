from django import forms


class SearchForm(forms.Form):
    query = forms.CharField()


class ClientSearchForm(forms.Form):
    query = forms.CharField(label='Phone',
        widget=forms.TextInput(attrs={'placeholder': 'name or +989123456789'})
    )


class BookIsbnSearchForm(forms.Form):
    query = forms.IntegerField(label='ISBN',
        widget=forms.TextInput(attrs={'placeholder': 'ISBN'})
    )
