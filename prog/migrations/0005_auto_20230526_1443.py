# Generated by Django 3.2.18 on 2023-05-26 12:43

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prog', '0004_log'),
    ]

    operations = [
        migrations.CreateModel(
            name='AET',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name="Nom de l'AET")),
                ('raspi_ip', models.CharField(blank=True, max_length=500, verbose_name='Addresse IP raspi')),
                ('mbed_list', models.TextField(blank=True, max_length=500, verbose_name="Liste mbed de l'AET")),
            ],
            options={
                'verbose_name': 'Statut AET',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='MbedFirmware',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Nom du soft mbed')),
                ('version', models.CharField(max_length=10, validators=[django.core.validators.RegexValidator('[0-9]{1,2}.[0-9]{2}$', 'Please respect version format (ex : 1.23)')], verbose_name='Version du soft')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='Modifié le')),
                ('filepath', models.FileField(upload_to='firmware/')),
            ],
        ),
        migrations.AddField(
            model_name='toolstatus',
            name='type',
            field=models.TextField(blank=True, max_length=50, verbose_name='Type'),
        ),
    ]
