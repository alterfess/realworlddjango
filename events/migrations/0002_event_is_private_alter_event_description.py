# Generated by Django 4.0.4 on 2022-05-04 08:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='is_private',
            field=models.BooleanField(default=False, verbose_name='Частное'),
        ),
        migrations.AlterField(
            model_name='event',
            name='description',
            field=models.TextField(default='', verbose_name='Описание'),
        ),
    ]
