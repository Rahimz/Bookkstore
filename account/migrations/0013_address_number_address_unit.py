# Generated by Django 4.0.1 on 2022-02-08 08:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0012_alter_customuser_default_billing_address_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='number',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='address',
            name='unit',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]