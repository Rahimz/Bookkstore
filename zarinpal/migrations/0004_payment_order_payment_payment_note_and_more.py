# Generated by Django 4.0.2 on 2022-02-22 05:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0032_purchase_paper_invoice_number'),
        ('zarinpal', '0003_alter_payment_ref_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments', to='orders.order'),
        ),
        migrations.AddField(
            model_name='payment',
            name='payment_note',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='reciept_image',
            field=models.ImageField(blank=True, upload_to='payments/receipts/'),
        ),
    ]