# Generated by Django 3.2.8 on 2021-10-17 21:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0004_product_productlocation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rack',
            name='cols',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='rack',
            name='name',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='rack',
            name='rows',
            field=models.PositiveIntegerField(default=1),
        ),
    ]