# Generated by Django 4.0.2 on 2022-03-07 06:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0046_orderline_cost_after_discount'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='orderline',
            options={'ordering': ('product__name',)},
        ),
        migrations.AlterModelOptions(
            name='purchase',
            options={'ordering': ('-created', '-payment_date', 'approved_date', '-pk')},
        ),
        migrations.AlterModelOptions(
            name='purchaseline',
            options={'ordering': ('product__name',)},
        ),
    ]
