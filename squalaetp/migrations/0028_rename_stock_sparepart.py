# Generated by Django 3.2 on 2021-04-20 13:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('squalaetp', '0027_xelon_is_active'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Stock',
            new_name='SparePart',
        ),
    ]