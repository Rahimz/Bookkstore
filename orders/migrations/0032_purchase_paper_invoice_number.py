# Generated by Django 4.0.2 on 2022-02-21 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0031_order_active_orderline_active_purchase_active_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='paper_invoice_number',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
