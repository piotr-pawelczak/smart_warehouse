# Generated by Django 3.2.8 on 2021-11-28 01:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0011_alter_location_max_load'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='max_load',
            field=models.DecimalField(decimal_places=3, default=100, max_digits=12),
        ),
    ]
