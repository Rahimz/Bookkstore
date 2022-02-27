# Generated by Django 4.0.2 on 2022-02-27 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0042_orderline_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalorder',
            name='qrcode',
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='qrcode',
            field=models.ImageField(blank=True, null=True, upload_to='orders/receipts'),
        ),
    ]
