# Generated by Django 3.1.2 on 2020-11-07 17:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('raspeedi', '0011_auto_20201104_1457'),
    ]

    operations = [
        migrations.CreateModel(
            name='Programing',
            fields=[
                ('psa_barcode', models.BigIntegerField(primary_key=True, serialize=False, verbose_name='référence boîtier')),
                ('peedi_path', models.CharField(max_length=20, verbose_name='dossier PEEDI')),
                ('peedi_dump', models.CharField(blank=True, max_length=25, verbose_name='dump PEEDI')),
                ('renesas_dump', models.CharField(blank=True, max_length=50, verbose_name='dump RENESAS')),
            ],
            options={
                'verbose_name': 'Données Programmation',
                'ordering': ['psa_barcode'],
            },
        ),
    ]
