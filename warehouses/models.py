from django.db import models
from django.conf import settings
# import uuid
from django.utils.translation import gettext_lazy as _
# from django.core.validators import MinValueValidator, MaxValueValidator
# from decimal import Decimal
from datetime import datetime

from products.models import Product
from orders.models import Order, Purchase
from account.models import CustomUser, Vendor


class Warehouse(models.Model):
    name = models.CharField(
        max_length=120,
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name



class Refund(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        default=0
    )
    discount = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        default=0
    )
    quantity = models.IntegerField(
        default=0
    )
    from_client = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        related_name='refund_client',
        null=True,
        blank=True
    )
    to_vendor = models.ForeignKey(
        Vendor,
        on_delete=models.SET_NULL,
        related_name='refund_vendor',
        null=True,
        blank=True
    )
    registrar = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='refund_registrar',
        blank=True,
        null=True
    )
    created = models.DateTimeField(
        auto_now_add=True
    )
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='refund_approver',
        blank=True,
        null=True
    )
    approved_date = models.DateTimeField(
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.order.pk} {self.product.name}"
