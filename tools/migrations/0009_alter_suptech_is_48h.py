# Generated by Django 3.2.24 on 2024-02-16 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0008_suptechfile_is_action'),
    ]

    operations = [
        migrations.AlterField(
            model_name='suptech',
            name='is_48h',
            field=models.BooleanField(default=False, verbose_name='Traitement 48h'),
        ),
    ]