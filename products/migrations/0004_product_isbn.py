# Generated by Django 4.0 on 2021-12-15 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_alter_product_publish_year'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='isbn',
            field=models.CharField(blank=True, max_length=13, null=True),
        ),
    ]