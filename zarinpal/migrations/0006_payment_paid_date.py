# Generated by Django 4.0.2 on 2022-03-02 06:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zarinpal', '0005_payment_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='paid_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
