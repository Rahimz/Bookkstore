from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
from django_countries.fields import Country, CountryField
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _
from django.shortcuts import reverse


class Address(models.Model):
    name = models.CharField(
        max_length=256,
        blank=True
    )
    street_address_1 = models.CharField(
        max_length=256,
        blank=True
    )
    street_address_2 = models.CharField(
        max_length=256,
        blank=True
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True
    )
    city = models.CharField(
        max_length=256,
        blank=True
    )

    country = CountryField()
    phone = PhoneNumberField(
        blank=True,
        default=""
    )

    class Meta:
        ordering = ("pk",)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('address_detail',
                       args=[self.id])
    def get_full_address(self):
        return f"{self.country.name} - {self.city} - {self.street_address_1}, {self.street_address_2} - {self.postal_code}"


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone = PhoneNumberField(
        blank=True,
        default=""
    )
    is_client= models.BooleanField(
        default=False
    )
    addresses = models.ManyToManyField(
        Address, blank=True,
        related_name="user_addresses"
    )
    default_shipping_address = models.ForeignKey(
        Address,
        related_name="shipping",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    default_billing_address = models.ForeignKey(
        Address,
        related_name="billing",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    date_joined = models.DateTimeField(
        default=timezone.now,
        editable=False
    )

    def get_absolute_url(self):
        return reverse('client_update',
                       args=[self.id])

    def __str__(self):
        if self.first_name or self.last_name:
            return ' - '.join([self.first_name, self.last_name])
        else:
            return self.username


class Vendor(CustomUser):
    overal_discount = models.DecimalField(
        max_digits=2,
        decimal_places=0,
        null=True,
        blank=True
    )
    contact_person = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    other_phone = PhoneNumberField(
        blank=True,
        default=""
    )

    class Meta:
        verbose_name = _('Vendor')
        verbose_name_plural = _('Vendors')


    def __str__(self):
        return self.first_name
