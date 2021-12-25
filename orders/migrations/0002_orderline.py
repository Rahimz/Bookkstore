# Generated by Django 4.0 on 2021-12-25 12:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0012_alter_good_state'),
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=12, max_digits=12)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('discount', models.DecimalField(decimal_places=12, max_digits=12)),
                ('good', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order_lines', to='products.good')),
                ('order', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='lines', to='orders.order')),
            ],
        ),
    ]
