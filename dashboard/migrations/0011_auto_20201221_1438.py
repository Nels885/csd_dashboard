# Generated by Django 3.1.3 on 2020-12-21 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0010_auto_20201106_1212'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weblink',
            name='type',
            field=models.CharField(choices=[('PSA', 'PSA'), ('OPEL', 'OPEL'), ('FORD', 'FORD'), ('RENAULT', 'RENAULT'), ('CLARION', 'CLARION'), ('VAG', 'VAG'), ('PARTS_SUPPLIERS', 'PARTS_SUPPLIERS'), ('AUTRES', 'AUTRES')], max_length=50, verbose_name='type'),
        ),
    ]