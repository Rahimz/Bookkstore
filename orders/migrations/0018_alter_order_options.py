# Generated by Django 4.0.1 on 2022-01-30 16:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0017_order_approved_date'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ('-approved_date', '-pk')},
        ),
    ]
