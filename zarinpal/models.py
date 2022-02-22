from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from orders.models import Order

class Payment(models.Model):
    client_name = models.CharField(max_length=150)
    client_phone = PhoneNumberField()
    amount = models.PositiveIntegerField()
    created = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        related_name='payments',
        null=True,
        blank=True
    )
    payment_note = models.TextField(
        null=True,
        blank=True
    )
    reciept_image = models.ImageField(
        upload_to='payments/receipts/',
        blank=True
    )
    ref_id = models.CharField(
        max_length=36,
        null=True,
        blank=True)

    def __str__(self):
        return self.client_name
