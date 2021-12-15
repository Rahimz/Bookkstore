# Generated by Django 4.0 on 2021-12-15 10:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_product_isbn'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='state',
            field=models.CharField(blank=True, choices=[('new', 'New'), ('used', 'Used'), ('children', 'children')], max_length=10, null=True),
        ),
    ]
