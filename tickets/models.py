from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from datetime import datetime
from django.core.validators import MinValueValidator , MaxValueValidator


from tools.gregory_to_hijry import hij_strf_date, greg_to_hij_date


class Ticket(models.Model):
    PRIORITY_CHOICES = (
        ('normal', _('Normal')),
        ('medium', _('Medium')),
        ('high', _('High')),
    )

    name = models.CharField(
        max_length=100,
    )
    description = models.TextField()
    priority = models.CharField(
        max_length=20,
        default='normal',
        choices=PRIORITY_CHOICES
    )
    rank = models.IntegerField(
        default=5,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
         ]
    )
    url = models.URLField(
        null=True,
        blank=True
    )
    file = models.FileField(
        upload_to='tickets/files',
        null=True,
        blank=True
    )
    created = models.DateTimeField(
        auto_now_add=True
    )
    updated = models.DateTimeField(
        auto_now=True
    )
    registrar = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='tickets_registrar',
        blank=True,
        null=True
    )
    active = models.BooleanField(
        default=True
    )
    is_checked = models.BooleanField(
        default=False
    )
    is_solved = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.name

    def get_fa_created(self):
        return hij_strf_date(greg_to_hij_date(self.created.date()), '%-d %B %Y')
