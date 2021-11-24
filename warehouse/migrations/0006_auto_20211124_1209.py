# Generated by Django 3.2.8 on 2021-11-24 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0005_alter_productlocation_lot_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='unit',
        ),
        migrations.RemoveField(
            model_name='warehouse',
            name='type',
        ),
        migrations.AddField(
            model_name='product',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='shelf',
            name='zone',
            field=models.CharField(choices=[('storage', 'Magazynowanie'), ('receiving', 'Przyjmowanie'), ('shipping', 'Wysyłka')], default='storage', max_length=20),
        ),
        migrations.AlterField(
            model_name='productlocation',
            name='lot_number',
            field=models.CharField(default='24/11/2021', max_length=10),
        ),
    ]
