# Generated by Django 3.2.8 on 2021-11-29 22:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0012_alter_location_max_load'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productlocation',
            name='lot_number',
            field=models.CharField(default='29/11/2021', max_length=10),
        ),
    ]
