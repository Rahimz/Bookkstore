# Generated by Django 4.0.1 on 2022-02-17 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0029_product_price_2_product_price_3_product_price_4_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='collection_set',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='is_collection',
            field=models.BooleanField(default=False),
        ),
    ]
