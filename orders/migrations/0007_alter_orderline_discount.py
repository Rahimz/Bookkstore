# Generated by Django 4.0.1 on 2022-01-10 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_order_paid_order_updated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderline',
            name='discount',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=12),
        ),
    ]
