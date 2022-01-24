# Generated by Django 4.0.1 on 2022-01-11 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_order_is_gift'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('draft', 'Draft'), ('paid', 'paid'), ('approved', 'approved'), ('unfulfilled', 'Unfulfilled'), ('fulfilled', 'Fulfilled'), ('canceled', 'Canceled')], default='unfulfilled', max_length=32),
        ),
    ]