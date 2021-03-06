# Generated by Django 4.0.1 on 2022-02-03 08:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0012_alter_customuser_default_billing_address_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orders', '0019_orderline_variation'),
    ]

    operations = [
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('approved_date', models.DateTimeField(blank=True, null=True)),
                ('payment_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('paid', 'paid'), ('approved', 'approved')], default='draft', max_length=32)),
                ('token', models.CharField(blank=True, max_length=36, unique=True)),
                ('total_cost', models.DecimalField(decimal_places=0, default=0, max_digits=12)),
                ('total_cost_after_discount', models.DecimalField(decimal_places=0, default=0, max_digits=12)),
                ('discount', models.DecimalField(decimal_places=0, default=0, max_digits=12)),
                ('payable', models.DecimalField(decimal_places=0, default=0, max_digits=12)),
                ('quantity', models.IntegerField(default=0)),
                ('paid', models.BooleanField(default=False)),
                ('approver', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchase_approver', to=settings.AUTH_USER_MODEL)),
                ('registrar', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchase_registerar', to=settings.AUTH_USER_MODEL)),
                ('vendor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='purchases', to='account.vendor')),
            ],
            options={
                'ordering': ('-payment_date', 'approved_date', '-pk'),
            },
        ),
    ]
