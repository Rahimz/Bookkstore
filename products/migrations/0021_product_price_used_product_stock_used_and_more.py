# Generated by Django 4.0.1 on 2022-01-22 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0020_product_available_in_store_product_available_online_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='price_used',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='product',
            name='stock_used',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(db_index=True, max_length=250, unique=True),
        ),
    ]