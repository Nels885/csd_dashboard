# Generated by Django 3.2.24 on 2024-02-21 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0009_alter_suptech_is_48h'),
    ]

    operations = [
        migrations.AddField(
            model_name='suptech',
            name='days_late',
            field=models.IntegerField(blank=True, null=True, verbose_name='jours de retard'),
        ),
    ]