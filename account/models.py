from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
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
    # id = models.AutoField(primary_key=True)
    pass


class Profile(models.Model):
    # In order to keep your code generic, use the get_user_model()
    # method to retrieve the user model and the AUTH_USER_MODEL setting
    # to refer to it when defining a model's relations to the user model,
    # instead of referring to the auth user model directly.
    GENDER_CHOICES = (('male', 'Male'),
                      ('female', 'Female'),
                      ('others', 'Others'),)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    gender = models.CharField(
        verbose_name='Gender',
        max_length=50,
        default='others',
        choices=GENDER_CHOICES,
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True
    )
    photo = models.ImageField(
        upload_to='users/%Y/%m/%d/',
        blank=True, null=True
    )

    def __str__(self):
        return 'Profile for user {}'.format(self.user.username)
