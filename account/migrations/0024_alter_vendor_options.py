# Generated by Django 4.0.2 on 2022-03-07 06:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0023_address_state'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='vendor',
            options={'ordering': ('first_name',), 'verbose_name': 'Vendor', 'verbose_name_plural': 'Vendors'},
        ),
    ]
