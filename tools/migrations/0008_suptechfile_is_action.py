# Generated by Django 3.2.23 on 2023-11-23 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0007_auto_20231110_1138'),
    ]

    operations = [
        migrations.AddField(
            model_name='suptechfile',
            name='is_action',
            field=models.BooleanField(default=False, verbose_name='action'),
        ),
    ]