# Generated by Django 3.2.8 on 2021-11-28 00:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0009_auto_20211126_1731'),
    ]

    operations = [
        migrations.CreateModel(
            name='InternalGoodsReceivedNote',
            fields=[
                ('document_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='documents.document')),
                ('document_type', models.CharField(default='PW', max_length=3)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('documents.document',),
        ),
    ]
