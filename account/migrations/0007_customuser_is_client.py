# Generated by Django 4.0 on 2022-01-07 06:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0006_delete_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_client',
            field=models.BooleanField(default=False),
        ),
    ]