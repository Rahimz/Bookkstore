# Generated by Django 4.0.1 on 2022-01-13 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zarinpal', '0002_alter_payment_ref_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='ref_id',
            field=models.CharField(blank=True, max_length=36, null=True),
        ),
    ]
