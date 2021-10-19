# Generated by Django 3.2.8 on 2021-10-19 13:42

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0003_shelf_shelf_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='column_index',
            field=models.SmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AddField(
            model_name='location',
            name='level_index',
            field=models.SmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]
