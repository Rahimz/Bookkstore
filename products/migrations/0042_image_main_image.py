# Generated by Django 4.0.2 on 2022-03-31 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0041_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='main_image',
            field=models.BooleanField(default=False),
        ),
    ]