# Generated by Django 4.0.1 on 2022-02-04 14:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0025_alter_product_vendor'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='vendor',
        ),
    ]
