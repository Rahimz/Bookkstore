# Generated by Django 4.0.1 on 2022-02-14 07:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0028_order_shipping_status_alter_order_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='purchaseline',
            options={'ordering': ('-pk', 'product')},
        ),
    ]
