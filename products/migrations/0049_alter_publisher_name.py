# Generated by Django 4.0.2 on 2022-04-08 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0048_publisher_product_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publisher',
            name='name',
            field=models.CharField(max_length=250, unique=True),
        ),
    ]
