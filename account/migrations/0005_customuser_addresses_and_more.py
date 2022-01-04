# Generated by Django 4.0 on 2021-12-25 06:46

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='addresses',
            field=models.ManyToManyField(blank=True, related_name='user_addresses', to='account.Address'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='default_billing_address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='account.address'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='default_shipping_address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='account.address'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='date_joined',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]