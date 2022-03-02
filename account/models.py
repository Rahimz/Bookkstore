from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
from django_countries.fields import Country, CountryField
from django_countries import countries
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _
from django.shortcuts import reverse

from simple_history.models import HistoricalRecords

class Address(models.Model):
    KIND_CHOICES = (
        ('billing', _('Billing')),
        ('shipping', _('Shipping'))
    )

    name = models.CharField(
        max_length=256,
        blank=True
    )
    address_phone = PhoneNumberField(
        blank=True,
        default=""
    )
    kind = models.CharField(
        max_length=25,
        choices=KIND_CHOICES,
        null=True,
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
    house_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )
    house_unit = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True
    )
    state = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    city = models.CharField(
        max_length=256,
        blank=True
    )

    country = CountryField()


    class Meta:
        ordering = ("pk",)

    def __str__(self):
        try:
            return self.name
        except:
            return ""

    def get_absolute_url(self):
        return reverse('address_detail',
                       args=[self.id])

    def get_full_address(self):
        try:
            if self.country == 'IR':
                return f"{self.country.name} {self.state if self.state else ''} {self.city} - {self.street_address_1} {self.street_address_2} {self.house_number if self.house_number else ''} {self.house_unit if self.house_unit else ''} {self.postal_code}"
            else:
                return f"No. {self.house_unit if self.house_unit else ''} {', ' + self.house_number if self.house_number else ''} \n{self.street_address_2},  {self.street_address_1}  \n{self.city} {', ' + self.state if self.state else ''} {dict(countries)[self.country.code]}"
        except:
            return ""


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone = PhoneNumberField(
        blank=True,
        default=""
    )
    phone_2 = PhoneNumberField(
        blank=True,
        null=True
    )
    is_client= models.BooleanField(
        default=False
    )
    is_manager = models.BooleanField(
        default = False
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
    social_media_name = models.CharField(
        max_length=100,
        blank=True,
        null=True
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

    def save(self, *args, **kwargs):
        if not self.overal_discount:
            self.overal_discount = 0
        super(Vendor, self).save(*args, **kwargs)

    def __str__(self):
        return self.first_name


class Credit(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
    )
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        null=True,
        blank=True
    )
    expiration_date = models.DateTimeField(
        null=True,
        blank=True
    )
    discount_percent = models.IntegerField(
        null=True,
        blank=True
    )
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.balance}"
