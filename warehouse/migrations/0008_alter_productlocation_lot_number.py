# Generated by Django 3.2.8 on 2021-11-26 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0007_auto_20211125_1237'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productlocation',
            name='lot_number',
            field=models.CharField(default='26/11/2021', max_length=10),
        ),
    ]
