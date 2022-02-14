from django.db import models
# from django.conf import settings
# import uuid
from django.utils.translation import gettext_lazy as _
# from django.core.validators import MinValueValidator, MaxValueValidator
# from decimal import Decimal
from datetime import datetime


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
