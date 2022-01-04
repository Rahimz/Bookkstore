from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from .models import CustomUser



class LoginForm(forms.Form):
	username = forms.CharField()
	password = forms.CharField(widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label=_('Password'),widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Repeat password'),
    widget=forms.PasswordInput)


    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'email')


    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError(_("Passwords don\'t match."))
        return cd['password2']


class UserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email')
