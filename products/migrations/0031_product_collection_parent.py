# Generated by Django 4.0.1 on 2022-02-17 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0030_product_collection_set_product_is_collection'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='collection_parent',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]