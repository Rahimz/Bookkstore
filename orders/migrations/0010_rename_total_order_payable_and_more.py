# Generated by Django 4.0.1 on 2022-01-12 05:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0009_alter_order_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='total',
            new_name='payable',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='total_net_amount',
            new_name='total_cost',
        ),
        migrations.AddField(
            model_name='order',
            name='total_cost_after_discount',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=12),
        ),
    ]