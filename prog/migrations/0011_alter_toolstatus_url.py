# Generated by Django 3.2.24 on 2024-03-26 16:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prog', '0010_alter_toolstatus_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='toolstatus',
            name='url',
            field=models.CharField(blank=True, max_length=500, verbose_name='Lien web'),
        ),
    ]
