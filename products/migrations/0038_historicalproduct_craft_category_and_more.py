# Generated by Django 4.0.2 on 2022-02-26 20:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0037_alter_craft_barcode_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalproduct',
            name='craft_category',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='craft_category',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='craft',
            name='barcode_number',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='historicalcraft',
            name='barcode_number',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
