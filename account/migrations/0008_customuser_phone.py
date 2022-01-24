# Generated by Django 4.0 on 2022-01-07 07:14

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0007_customuser_is_client'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='phone',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, default='', max_length=128, region=None),
        ),
    ]