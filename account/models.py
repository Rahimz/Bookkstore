from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
from django_countries.fields import Country, CountryField
from phonenumber_field.modelfields import PhoneNumberField


class Address(models.Model):
    first_name = models.CharField(
        max_length=256,
        blank=True
    )
    last_name = models.CharField(
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
    city = models.CharField(
        max_length=256,
        blank=True
    )
    city_area = models.CharField(
        max_length=128,
        blank=True
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True
    )
    country = CountryField()
    country_area = models.CharField(
        max_length=128,
        blank=True
    )
    phone = PhoneNumberField(
        blank=True,
        default=""
    )

    class Meta:
        ordering = ("pk",)

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)

    def get_absolute_url(self):
        return reverse('address_detail',
                       args=[self.id])


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
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    default_billing_address = models.ForeignKey(
        Address,
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    date_joined = models.DateTimeField(
        default=timezone.now,
        editable=False
    )

    def __str__(self):
        if self.first_name or self.last_name:
            return ' - '.join([self.first_name, self.last_name])
        else:
            return self.username
