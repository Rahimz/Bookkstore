# Generated by Django 4.0.1 on 2022-01-31 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0023_product_isbn_9'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='publisher_2',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
