# Generated by Django 4.0.1 on 2022-01-22 10:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0021_product_price_used_product_stock_used_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='price_1',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='product',
            name='stock_1',
            field=models.IntegerField(default=0),
        ),
    ]