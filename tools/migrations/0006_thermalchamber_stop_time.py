# Generated by Django 3.0.8 on 2020-07-31 07:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0005_thermalchamber_xelon_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='thermalchamber',
            name='stop_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='heure de fin'),
        ),
    ]
