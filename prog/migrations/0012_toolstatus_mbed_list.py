# Generated by Django 3.2.25 on 2024-08-20 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prog', '0011_alter_toolstatus_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='toolstatus',
            name='mbed_list',
            field=models.TextField(blank=True, max_length=500, verbose_name="Liste mbed de l'AET"),
        ),
    ]
