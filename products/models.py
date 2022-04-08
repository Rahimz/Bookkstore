from django.db import models
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
import string
import random
from django.conf import settings

from simple_history.models import HistoricalRecords

from files.models import ImportSession
from account.models import Vendor
# from discount.models import Cupon
# from warehouse.models import warehouse


def rand_slug():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))


class Category(models.Model):
    parent_category = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    name = models.CharField(
        max_length=250,
        # unique=True,
        db_index=True,
    )
    slug = models.SlugField(
        max_length=300,
        # unique=True,
        allow_unicode=True
    )
    active = models.BooleanField(
        default=True,
    )
    is_main = models.BooleanField(
        default=False
    )
    is_sub = models.BooleanField(
        default=False
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def get_sub_category(self):
        return self.category_set.all()

    def get_absolute_url(self):
        return reverse('shop:products_list',
                       args=[self.slug])

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super(Category, self).save(*args, **kwargs)


class Publisher(models.Model):
    name = models.CharField(
        max_length=250,
        unique=True
    )
    active = models.BooleanField(
        default=True
    )
    url = models.URLField(
        blank=True,
        null=True
    )
    product_count = models.IntegerField(
        null=True,
        blank=True
    )
    created = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return self.name


class Product(models.Model):
    STATE_CHOICES = [
        ('new', _('New')),
        ('used', _('Used')),
    ]
    AGE_RANGE_CHOICES = [
        ('-', ''),
        ('1', '0-2'),
        ('2', '2-4'),
        ('3', '4-6'),
        ('4', '6-8'),
        ('5', '8-10'),
    ]
    PRODUCT_TYPE_CHOICES = [
        ('book', _('Book')),
        ('craft', _('Craft')),
    ]

    # Meta data for an object
    import_session = models.ForeignKey(
        ImportSession,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    category = models.ForeignKey(
        Category,
        related_name='product',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    sub_category = models.ForeignKey(
        Category,
        related_name='product_sub',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    craft_category = models.CharField(
        max_length=150,
        null=True,
        blank=True
    )
    name = models.CharField(
        max_length=500,
        db_index=True
    )
    collection_name = models.CharField(
        max_length=300,
        null=True,
        blank=True
    )
    number_in_collection = models.CharField(
        max_length=100,
        null=True,
        blank=True
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
    isbn_9 = models.CharField(
        max_length=9,
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
    latin_name = models.CharField(
        max_length=300,
        blank=True,
        null=True
    )
    author_latin_name = models.CharField(
        max_length=300,
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
    about = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )
    description = models.TextField(
        blank=True,
        null=True
    )
    is_collection = models.BooleanField(
        default=False
    )
    collection_set = models.TextField(
        null=True,
        blank=True
    )
    collection_parent = models.CharField(
        max_length=13,
        null=True,
        blank=True
    )
    age_range = models.CharField(
        max_length=150,
        default='',
        choices=AGE_RANGE_CHOICES,
    )

    # warehouse = models.ForeignKey(
    #     Warehouse,
    #     on_delete=SET_NULL,
    #     blank=True,
    #     null=True,
    # )
    zero_stock = models.BooleanField(
        default=False,
    )
    zero_stock_limit = models.IntegerField(
        null=True,
        blank=True
    )
    product_type = models.CharField(
        max_length=100,
        choices=PRODUCT_TYPE_CHOICES,
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
    page_number = models.IntegerField(
        default=0,
    )
    publisher = models.CharField(
        max_length=250,
        null=True,
        blank=True
    )
    publisher_2 = models.CharField(
        max_length=250,
        null=True,
        blank=True
    )
    pub_1 = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        related_name='productPub_1',
        null=True,
        blank=True,
    )
    pub_2 = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        related_name='productPub_2',
        null=True,
        blank=True,
    )
    publish_year = models.IntegerField(
        # default=1400,
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
        decimal_places=0,
        default=0
    )
    stock = models.IntegerField(
        default=0,
    )
    has_other_prices = models.BooleanField(
        default=False
    )
    price_1 = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        default=0
    )
    stock_1 = models.IntegerField(
        default=0,
    )
    price_2 = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        default=0
    )
    stock_2 = models.IntegerField(
        default=0,
    )
    price_3 = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        default=0
    )
    stock_3 = models.IntegerField(
        default=0,
    )
    price_4 = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        default=0
    )
    stock_4 = models.IntegerField(
        default=0,
    )
    price_5 = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        default=0
    )
    stock_5 = models.IntegerField(
        default=0,
    )
    price_used = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        default=0
    )
    stock_used =  models.IntegerField(
        default=0,
    )
    # discount = models.ForeignKey(
    #     Coupon,
    #     on_delete=models.SET_NULL,
    #     blank=True,
    #     null=True,
    # )
    store_positon = models.CharField(
        max_length=8,
        blank=True,
        null=True
    )
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    vendors = models.ManyToManyField(
        Vendor,
        blank=True,
        related_name='products_vendor'
    )
    # vendor = models.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True
    # )
    admin_note = models.TextField(
        blank=True,
        null=True,
    )
    available = models.BooleanField(
        default=True
    )
    available_in_store = models.BooleanField(
        default=True
    )
    available_online = models.BooleanField(
        default=True
    )
    created = models.DateTimeField(
        auto_now_add=True
    )
    updated = models.DateTimeField(
        auto_now=True
    )
    history = HistoricalRecords()

    class Meta:
        ordering = ('-updated', '-created',)
        index_together = (('id', 'slug'),)

    def get_absolute_url(self):
        return reverse('shop:product_detail',
                       args=[self.id, self.slug])

    def save(self, *args, **kwargs):
        if self.image and not self.image_alt:
            self.image_alt = self.name

        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)

        if self.isbn and not self.isbn_9:
            if len(self.isbn) == 13:
                self.isbn_9 = self.isbn[3:-1]
            elif len(self.isbn) == 10:
                self.isbn_9 = self.isbn[:-1]
            elif len(self.isbn) == 9:
                self.isbn_9 = self.isbn

        # check all stock to remove price from zero stock

        # if self.stock_1 == 0:
        #     self.price_1 = 0
        #
        # if self.stock_2 == 0:
        #     self.price_2 = 0
        #
        # if self.stock_3 == 0:
        #     self.price_3 = 0
        #
        # if self.stock_4 == 0:
        #     self.price_4 = 0
        #
        # if self.stock_5 == 0:
        #     self.price_5 = 0
        #
        # if self.stock_used == 0:
        #     self.price_used = 0

        if self.collection_set:
            self.is_collection = True

        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        if self.collection_name:
            return f"{self.collection_name}, {self.number_in_collection if self.number_in_collection else ''}, {self.name}"
        else:
            return self.name

    def get_other_stock(self):
        return sum([self.stock_1, self.stock_2, self.stock_3, self.stock_4, self.stock_5])


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
        default='new',
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


class Craft(models.Model):
    name = models.CharField(
        max_length=250,
    )
    slug = models.SlugField(
        max_length=550,
        db_index=True,
        allow_unicode=True
    )
    barcode_number = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    category = models.CharField(
        max_length = 100,
        null=True,
        blank=True,
    )
    weight = models.FloatField(
        null=True,
        blank=True
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        default=0
    )
    stock = models.IntegerField(
        default=0,
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
        null=True,
        blank=True
    )
    created = models.DateTimeField(
        auto_now_add=True
    )
    available = models.BooleanField(
        default=True
    )
    available_in_store = models.BooleanField(
        default=True
    )
    available_online = models.BooleanField(
        default=False
    )
    history = HistoricalRecords()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.image and not self.image_alt:
            self.image_alt = self.name

        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)

        super(Craft, self).save(*args, **kwargs)


class Image(models.Model):
    VARIATION_CHOICES =(
        ('new', _('New')),
        ('used', _('Used')),
        ('', ''),
    )
    name = models.CharField(
        max_length=150,
    )
    product = models.ForeignKey(
        Product,
        related_name='images',
        on_delete=models.CASCADE
    )
    file = models.ImageField(
        upload_to='products/images/',
    )
    image_alt = models.CharField(
        max_length=300,
        blank=True,
        null=True
    )
    variation = models.CharField(
        max_length=25,
        choices=VARIATION_CHOICES,
        default='new',
    )
    registrar = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    main_image = models.BooleanField(
        default=False
    )
    active = models.BooleanField(
        default=True
    )
    created = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.image_alt:
            self.image_alt = str(self.product)

        super(Image, self).save(*args, **kwargs)


    # def get_absolute_url(self):
    #     return reverse('shop:product_image',
    #                    args=[self.id, self.slug])
