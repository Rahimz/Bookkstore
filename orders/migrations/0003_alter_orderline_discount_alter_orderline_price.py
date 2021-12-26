# Generated by Django 4.0 on 2021-12-25 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_orderline'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderline',
            name='discount',
            field=models.DecimalField(decimal_places=0, max_digits=12),
        ),
        migrations.AlterField(
            model_name='orderline',
            name='price',
            field=models.DecimalField(decimal_places=0, max_digits=12),
        ),
    ]
