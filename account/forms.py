from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from .models import CustomUser, Vendor, Address



class LoginForm(forms.Form):
	username = forms.CharField()
	password = forms.CharField(widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label=_('Password'),widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Repeat password'),
    widget=forms.PasswordInput)


    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email')


    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError(_("Passwords don\'t match."))
        return cd['password2']


class UserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email')


class ClientAddForm(forms.ModelForm):
	class Meta:
		model = CustomUser
		fields = ('first_name', 'last_name', 'phone')


class ClientUpdateForm(forms.ModelForm):

	class Meta:
		model = CustomUser
		fields = (
			'username', 'first_name', 'last_name', 'phone', 'email',
			'default_billing_address', 'default_shipping_address', 'addresses'

		)

class VendorAddForm(forms.ModelForm):
	class Meta:
		model = Vendor
		fields = ('first_name', 'overal_discount', 'phone', 'contact_person', 'other_phone')
		labels = {
            'first_name': _('Name'),
			'overal_discount': _('Overal discount'),
			'default_billing_address': _('Address'),
			'contact_person': _('Contact person'),
			'other_phone': _('Other phone')
        }
		widgets = {
        	'overal_discount': forms.TextInput(attrs={'placeholder': _('Percent')})
        }

class AddressAddForm(forms.ModelForm):
	class Meta:
		model = Address
		exclude = ['name', 'phone']
		# labels = {
        #     'first_name': _('Name'),
		# 	'overal_discount': _('Overal discount'),
		# 	'default_billing_address': _('Address'),
		# 	'contact_person': _('Contact person'),
		# 	'other_phone': _('Other phone')
        # }
		# widgets = {
        # 	'overal_discount': forms.TextInput(attrs={'placeholder': _('Percent')})
        # }
