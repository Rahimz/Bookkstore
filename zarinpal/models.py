from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

class Payment(models.Model):
    client_name = models.CharField(max_length=150)
    client_phone = PhoneNumberField()
    amount = models.PositiveIntegerField()
    created = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    ref_id = models.CharField(
        max_length=36,
        null=True,
        blank=True)
    
    def __str__(self):
        return self.client_name
