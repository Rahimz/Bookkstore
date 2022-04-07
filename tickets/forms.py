from django import forms
from django.utils.translation import gettext_lazy as _
# from django.core.validators import MinValueValidator, MaxValueValidator

from .models import Ticket


class CreateTicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = [
            'name', 'priority', 'rank',
            'description',
            'url', 'file',
        ]
        widgets = {
            'url': forms.TextInput(attrs={'placeholder': _('The URL of the page that has the problem')})
        }
        help_texts ={
            'file': _('The file or screenshot that help to find the problem'),
            'rank': _('select from 1 to 10 tha 1 is the highest rank and 10 is the lowest rank'),

        }
        # validators = {
        #     'rank': [MinValueValidator(1), MaxValueValidator(10)]
        # }
