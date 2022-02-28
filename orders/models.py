from django.db import models
from django.conf import settings
import uuid
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from datetime import datetime
from math import trunc

from phonenumber_field.modelfields import PhoneNumberField
from simple_history.models import HistoricalRecords

from account.models import Address, Vendor
from products.models import Product
from tools.gregory_to_hijry import hij_strf_date, greg_to_hij_date


PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100)]

class Order(models.Model):
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('paid', _('Paid')),
        ('approved', _('Approved')),
        ('unfulfilled', _('Unfulfilled')),
        ('fulfilled', _('Fulfilled')),
        ('canceled', _('Canceled')),
    ]
    SHIPPING_METHODS = [
        ('post', _('Post')),
        ('bike_delivery', _('Bike Delivery')),
        ('pickup', _('Pickup'))
    ]
    SHIPPING_STATUS =(
        ('', ''),
        ('semi', _('Semi shipped')),
        ('full', _('Fully Shipped')),
    )
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
        default='draft',
        choices=STATUS_CHOICES
    )
    channel = models.CharField(
        max_length=50,
        default = 'cashier',
        choices=CHANNEL_CHOICES,
    )
    billing_address = models.ForeignKey(
        Address,
        related_name='order_billing',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    shipping_address = models.ForeignKey(
        Address,
        related_name='order_shipping',
        null=True,
        blank=True,
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

    )
    shipping_time = models.CharField(
        max_length=250,
        null=True,
        blank=True
    )
    shipped_code = models.CharField(
        max_length=24,
        blank=True,
        null=True
    )
    shipping_status = models.CharField(
        max_length=50,
        choices=SHIPPING_STATUS,
        default='',
        blank=True,
        null=True
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
    pay_by_credit = models.BooleanField(
        default=False
    )
    credit = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0,
    )
    active = models.BooleanField(
        default= True
    )
    pay_receipt = models.ImageField(
        upload_to='orders/receipts',
        null=True,
        blank=True
    )
    qrcode = models.ImageField(
        upload_to='orders/receipts',
        null=True,
        blank=True
    )
    history = HistoricalRecords()

    class Meta:
        ordering = ("-approved_date", "-pk",)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = str(uuid.uuid4())

        self.quantity = self.get_total_quantity()
        self.weight = self.get_total_weight()

        self.payable = self.get_payable()

        if not self.billing_address:
            if self.client:
                self.billing_address = self.client.default_billing_address
        if not self.shipping_address:
            if self.client:
                self.billing_address = self.client.default_shipping_address
        super(Order, self).save(*args, **kwargs)

    def __str__(self):
        return "#%d" % (self.id,)

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.lines.all())

    def get_cost_after_discount(self):
        return sum(item.get_cost_after_discount() for item in self.lines.all())

    def get_payable(self):
        return self.get_cost_after_discount() - self.discount + self.shipping_cost

    def get_total_weight(self):
        return sum(item.get_weight() for item in self.lines.all())

    def get_total_quantity(self):
        return sum(item.quantity for item in self.lines.all())

    def get_total_discount(self):
        return sum(item.discount for item in self.lines.all())

    def get_fa_approved(self):
        if self.approved_date:
            return hij_strf_date(greg_to_hij_date(self.approved_date.date()), '%-d %B %Y')
        else:
            return
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
        # default=0
        null=True,
        blank=True
    )
    variation = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )
    shipped =  models.BooleanField(
        default=False,
    )
    shipped_date = models.DateTimeField(
        null=True,
        blank=True
    )
    active = models.BooleanField(
        default= True
    )
    created = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ("-product",)


    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.quantity

    def get_cost_after_discount(self):
        if self.discount:
            return self.price * self.quantity - self.discount
        else:
            return self.price * self.quantity

    def get_weight(self):
        if self.product.weight:
            return int(self.product.weight * self.quantity)
        else:
            return 0

    def update_quantity(self, new_quantity):
        self.quantity = new_quantity

    def update_discount(self, new_discount):
        self.discount = new_discount

    def save(self, *args, **kwargs):
        if not self.created:
            self.created = self.order.created

        super(OrderLine, self).save(*args, **kwargs)


class Purchase(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('paid', 'paid'),
        ('approved', 'approved'),
    ]

    # is used to register the staff activity
    registrar = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='purchase_registerar',
        blank=True,
        null=True
    )
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='purchase_approver',
        blank=True,
        null=True
    )
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.SET_NULL,
        related_name='purchases',
        blank=True,
        null=True,
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        auto_now=True
    )
    approved_date = models.DateTimeField(
        blank=True,
        null=True
    )
    payment_date = models.DateField(
        blank=True,
        null=True
    )
    deadline_days = models.IntegerField(
        blank=True,
        null=True
    )
    paper_invoice_number = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=32,
        default='draft',
        choices=STATUS_CHOICES
    )
    token = models.CharField(
        max_length=36,
        unique=True,
        blank=True
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
    discount_percent = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
        # null=True,
        # blank=True,
    )
    payable = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0,
    )
    quantity = models.IntegerField(
        default=0,
    )
    paid = models.BooleanField(default=False)
    active = models.BooleanField(
        default= True
    )

    class Meta:
        ordering = ("-payment_date", "approved_date", "-pk",)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = str(uuid.uuid4())

        self.quantity = self.get_total_quantity()

        # managing discounts
        if self.discount == 0 and self.discount_percent != 0:
            self.discount =  self.get_cost_after_discount() * self.discount_percent / 100
        elif self.discount and not self.discount_percent:
            self.discount_percent = round(self.discount / self.get_cost_after_discount() * 100, 1)
        elif self.discount and self.discount_percent:
            if round(self.discount / self.get_cost_after_discount() * 100, 1) != self.discount_percent:
                self.discount_percent = round(self.discount / self.get_cost_after_discount() * 100, 1)

        # self.payable = self.get_payable() - self.discount
        self.payable = self.get_cost_after_discount() - self.discount


        super(Purchase, self).save(*args, **kwargs)

    def __str__(self):
        return self.vendor.first_name

    def get_remained_days(self):
        return (self.payment_date - datetime.now().date()).days

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.lines.all())

    def get_cost_after_discount(self):
        return sum(item.get_cost_after_discount() for item in self.lines.all())

    def get_payable(self):
        return self.get_cost_after_discount() - self.discount - (self.get_cost_after_discount() * self.discount_percent/100)

    def get_total_weight(self):
        return sum(item.get_weight() for item in self.lines.all())

    def get_total_quantity(self):
        return sum(item.quantity for item in self.lines.all())

    def get_fa_approved(self):
        return hij_strf_date(greg_to_hij_date(self.approved_date.date()), '%-d %B %Y')

    def get_fa_created(self):
        return hij_strf_date(greg_to_hij_date(self.created.date()), '%-d %B %Y')

    def get_fa_payment(self):
        return hij_strf_date(greg_to_hij_date(self.payment_date), '%-d %B %Y')


class PurchaseLine(models.Model):
    purchase = models.ForeignKey(
        Purchase,
        related_name='lines',
        editable=False,
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        related_name='purchase_lines',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    price = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        null=True,
        blank=True
    )
    quantity = models.PositiveIntegerField(
        default=0
    )
    discount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0
    )
    discount_percent = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=0,
        validators=PERCENTAGE_VALIDATOR,
        # null=True,
        # blank=True,
    )
    variation = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )
    active = models.BooleanField(
        default= True
    )

    class Meta:
        ordering = ("-pk", "product")


    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        if self.discount == 0 and self.discount_percent != 0:
            self.discount =  self.price * self.discount_percent / 100
        elif self.discount and not self.discount_percent:
            self.discount_percent = round(self.discount / self.price * 100, 1)
        elif self.discount and self.discount_percent:
            if round(self.discount / self.price * 100, 1) != self.discount_percent:
                self.discount_percent = round(self.discount / self.price * 100, 1)

        super(PurchaseLine, self).save(*args, **kwargs)

    def get_cost(self):
        return self.price * self.quantity

    def get_cost_after_discount(self):
        if self.discount_percent:
            return self.get_cost() - self.get_cost() * self.discount_percent / 100
        else:
            return (self.price - self.discount) * self.quantity

    def get_weight(self):
        return self.product.weight * self.quantity

    def update_quantity(self, new_quantity):
        self.quantity = new_quantity

    def update_discount(self, new_discount):
        self.discount = new_discount
