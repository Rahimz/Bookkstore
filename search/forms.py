from django import forms


class SearchForm(forms.Form):
    query = forms.CharField()


class ClientSearchForm(forms.Form):
    query = forms.CharField(label='Phone',
        widget=forms.TextInput(attrs={'placeholder': 'name or +989123456789'})
    )
