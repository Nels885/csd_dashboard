# Generated by Django 3.2.12 on 2022-03-28 10:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reman', '0030_alter_default_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='repair',
            name='diagnostic_data',
            field=models.TextField(blank=True, max_length=50000, verbose_name='Données Diagnostique'),
        ),
    ]