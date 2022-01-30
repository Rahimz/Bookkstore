from django.db import models
from django.conf import settings
import uuid
from django.utils.translation import gettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField

from account.models import Address
from products.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('paid', 'paid'),
        ('approved', 'approved'),
        ('unfulfilled', 'Unfulfilled'),
        ('fulfilled', 'Fulfilled'),
        ('canceled', 'Canceled'),
    ]
    SHIPPING_METHODS = [
        ('post', 'Post'),
        ('bike_delivery', 'Bike Delivery'),
        ('pickup', 'Pickup')
    ]
    CHANNEL_CHOICES = [
        ('cashier', _('Cashier')),
        ('instagram', 'Instagram'),
        ('telegram', 'Telegram'),
        ('twitter', 'Twitter'),
        ('Website', _('Website')),
        ('other', _('Other')),
    ]

    # is used to register the staff activity
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='admin_orders',
        blank=True,
        null=True
    )
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='orders',
        blank=True,
        null=True
    )
    client_phone = PhoneNumberField(
        blank=True,
        default=""
    )
    created = models.DateTimeField(
        auto_now_add=True,
        editable=False,
    )
    updated = models.DateTimeField(
        auto_now=True
    )
    approved_date = models.DateTimeField(
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=32,
        default='unfulfilled',
        choices=STATUS_CHOICES
    )
    channel = models.CharField(
        max_length=50,
        default = 'cashier',
        choices=CHANNEL_CHOICES,
    )
    billing_address = models.ForeignKey(
        Address,
        related_name="+",
        editable=False,
        null=True,
        on_delete=models.SET_NULL
    )
    shipping_address = models.ForeignKey(
        Address,
        related_name="+",
        editable=False,
        null=True,
        on_delete=models.SET_NULL
    )
    user_email = models.EmailField(
        blank=True,
        default=""
    )
    token = models.CharField(
        max_length=36,
        unique=True,
        blank=True
    )
    # Token of a checkout instance that this order was created from
    checkout_token = models.CharField(
        max_length=36,
        blank=True
    )
    shipping_method = models.CharField(
        max_length=100,
        default='post',
        choices=SHIPPING_METHODS,
    )
    shipping_cost = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0,
        editable=False,
    )
    total_cost = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0,
    )
    total_cost_after_discount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0,
    )
    discount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0,
    )
    payable = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0,
    )
    customer_note = models.TextField(
        blank=True,
        default=""
    )
    weight = models.IntegerField(
        default=0,
        blank=True,
    )
    quantity = models.IntegerField(
        default=0,
    )
    is_gift = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)

    class Meta:
        ordering = ("-approved_date", "-pk",)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = str(uuid.uuid4())

        self.quantity = self.get_total_quantity()

        self.payable = self.get_cost_after_discount() - self.discount

        super(Order, self).save(*args, **kwargs)

    def __str__(self):
        return "#%d" % (self.id,)

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.lines.all())

    def get_cost_after_discount(self):
        return sum(item.get_cost_after_discount() for item in self.lines.all())

    def get_payable(self):
        return self.get_cost_after_discount() - self.discount

    def get_total_weight(self):
        return sum(item.get_weight() for item in self.lines.all())

    def get_total_quantity(self):
        return sum(item.quantity for item in self.lines.all())

    # def get_absolute_url(self):
    #     return reverse('shop:product_detail',
    #                    args=[self.id])


class OrderLine(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='lines',
        editable=False,
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        related_name='order_lines',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    price = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES
    )
    quantity = models.PositiveIntegerField(
        default=0
    )
    discount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0
    )

    class Meta:
        ordering = ("-product",)


    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.quantity

    def get_cost_after_discount(self):
        return self.price * self.quantity - self.discount

    def get_weight(self):
        return self.product.weight * self.quantity

    def update_quantity(self, new_quantity):
        self.quantity = new_quantity

    def update_discount(self, new_discount):
        self.discount = new_discount
