# Generated by Django 4.0.1 on 2022-02-04 14:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0027_product_vendo'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='vendo',
            new_name='vendor',
        ),
    ]
