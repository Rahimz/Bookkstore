# Generated by Django 4.0.2 on 2022-02-28 08:03

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0043_historicalorder_qrcode_order_qrcode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchaseline',
            name='discount_percent',
            field=models.DecimalField(decimal_places=1, default=0, max_digits=4, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
    ]