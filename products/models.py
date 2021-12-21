from django.db import models
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
import string
import random

from files.models import ImportSession


def rand_slug():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))


class Category(models.Model):
    name = models.CharField(
        max_length=250,
        db_index=True,
    )
    slug = models.SlugField(
        max_length=300,
        unique=True,
        allow_unicode=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    # def get_absolute_url(self):
    #     return reverse('shop:product_list_by_category',
    #                    args=[self.slug])

    def __str__(self):
        return self.name


class Product(models.Model):
    # Meta data for an object
    import_session = models.ForeignKey(
        ImportSession,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    STATE_CHOICES = [
        ('new', _('New')),
        ('used', _('Used')),
    ]

    category = models.ForeignKey(
        Category,
        related_name='product',
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        max_length=500,
        db_index=True
    )
    slug = models.SlugField(
        max_length=550,
        db_index=True,
        allow_unicode=True
    )
    barcode_number = models.CharField(
        max_length=13,
        blank=True,
        null=True
    )
    isbn = models.CharField(
        max_length=13,
        blank=True,
        null=True
    )
    author = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )
    translator = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )
    illustrator = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )
    image = models.ImageField(
        upload_to='products/images/',
        blank=True
    )
    image_alt = models.CharField(
        max_length=300,
        blank=True,
        null=True
    )
    description = models.TextField(
        blank=True,
        null=True
    )
    stock = models.IntegerField(
        default=0,
    )
    product_type = models.CharField(
        max_length=250,
        null=True,
        blank=True
    )
    state = models.CharField(
        max_length=10,
        default='new',
        choices=STATE_CHOICES
    )
    weight = models.FloatField(
        default=0,
        null=True,
        blank=True
    )
    size = models.CharField(
        max_length=250,
        null=True,
        blank=True
    )
    cover_type = models.CharField(
        max_length=250,
        null=True,
        blank=True
    )
    publisher = models.CharField(
        max_length=250,
        null=True,
        blank=True
    )
    publish_year = models.IntegerField(
        default=1400,
        validators=[MinValueValidator(1233), MaxValueValidator(1400)],
        null=True,
        blank=True
    )
    edition = models.IntegerField(
        null=True,
        blank=True,
    )
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        null=True,
        blank=True
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=0
    )
    available = models.BooleanField(
        default=True
    )
    created = models.DateTimeField(
        auto_now_add=True
    )
    updated = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ('-created',)
        index_together = (('id', 'slug'),)

    def get_absolute_url(self):
        return reverse('shop:product_detail',
                       args=[self.id])

    def save(self, *args, **kwargs):
        if self.image and not self.image_alt:
            self.image_alt = self.name

        if not self.slug:
            self.slug = slugify(rand_slug() + "-" + self.name, allow_unicode=True)
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Good(models.Model):
    STATE_CHOICES = [
        ('new', _('New')),
        ('used', _('Used')),
    ]

    product = models.ForeignKey(
        Product,
        related_name='goods',
        on_delete=models.CASCADE,
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        default=0
    )
    stock = models.IntegerField(
        default=0,
    )
    state = models.CharField(
        max_length=10,
        default = 'new',
        choices=STATE_CHOICES
    )
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        null=True,
        blank=True
    )
    edition = models.IntegerField(
        null=True,
        blank=True,
    )
    available = models.BooleanField(
        default=True
    )
    created = models.DateTimeField(
        auto_now_add=True
    )
    updated = models.DateTimeField(
        auto_now=True
    )
    cover_type = models.CharField(
        max_length=250,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ('-updated',)

    def __str__(self):
        return self.product.name

    def save(self,  *args, **kwargs):
        if not self.price:
            self.price = self.product.price
        

        if self.state == 'used' and not self.price:
            self.price = self.product.price / 2

        if not self.purchase_price:
            self.purchase_price = self.product.purchase_price

        if not self.cover_type:
            self.cover_type = self.product.cover_type

        super(Good, self).save(*args, **kwargs)
