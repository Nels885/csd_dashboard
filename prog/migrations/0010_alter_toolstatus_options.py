# Generated by Django 3.2.24 on 2024-03-11 11:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('prog', '0009_auto_20240307_0920'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='toolstatus',
            options={'ordering': ['name'], 'permissions': [('view_info_tools', 'Can view info tools')], 'verbose_name': 'Statut Outil'},
        ),
    ]
