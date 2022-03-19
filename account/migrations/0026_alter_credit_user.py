# Generated by Django 4.0.2 on 2022-03-19 12:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0025_customuser_is_online_manager'),
    ]

    operations = [
        migrations.AlterField(
            model_name='credit',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='credit', to=settings.AUTH_USER_MODEL),
        ),
    ]
