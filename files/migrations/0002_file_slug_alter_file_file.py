# Generated by Django 4.0 on 2021-12-15 06:11

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='slug',
            field=models.SlugField(allow_unicode=True, default=django.utils.timezone.now, max_length=150, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='file',
            name='file',
            field=models.FileField(upload_to='media/files/upload/'),
        ),
    ]
