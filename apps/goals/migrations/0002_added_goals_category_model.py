# Generated by Django 4.1.7 on 2023-05-01 17:41
from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goals', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goalcategory',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='goalcategory',
            name='updated',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата последнего обновления'),
        ),
    ]