from django import forms


class SearchForm(forms.Form):
    query = forms.CharField()


class ClientSearchForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['query'].required = False

    query = forms.CharField(label='Phone',
        widget=forms.TextInput(attrs={'placeholder': 'name or +989123456789'})
    )


class BookIsbnSearchForm(forms.Form):
    isbn_query = forms.IntegerField(label='ISBN',
        widget=forms.TextInput(attrs={'placeholder': 'ISBN'})
    )
