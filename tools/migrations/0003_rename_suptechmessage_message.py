# Generated by Django 3.2.19 on 2023-06-28 07:35

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
        ('tools', '0002_auto_20230419_1002'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='SuptechMessage',
            new_name='Message',
        ),
    ]
