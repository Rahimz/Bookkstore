# Generated by Django 4.0.2 on 2022-02-26 06:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0041_alter_orderline_discount'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderline',
            name='created',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]