# Generated by Django 3.2.8 on 2021-11-28 00:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0010_auto_20211128_0010'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='max_load',
            field=models.DecimalField(decimal_places=2, default=100, max_digits=12),
        ),
    ]