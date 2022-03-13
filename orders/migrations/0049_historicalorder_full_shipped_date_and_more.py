# Generated by Django 4.0.2 on 2022-03-13 05:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0048_historicalpurchaseline_historicalpurchase_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalorder',
            name='full_shipped_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='full_shipped_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
