# Generated by Django 4.0.1 on 2022-02-04 13:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0012_alter_customuser_default_billing_address_and_more'),
        ('products', '0024_product_publisher_2'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='vendor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='account.vendor'),
        ),
    ]