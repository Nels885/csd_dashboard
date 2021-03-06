# Generated by Django 3.1.2 on 2020-11-12 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('psa', '0002_auto_20201107_1811'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='current_cal',
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(choices=[('RT3', 'RT3'), ('RT4', 'RT4'), ('RT5', 'RT5'), ('RT6', 'RT6 / RNEG2'), ('RT6v2', 'RT6v2 / RNEG2'), ('SMEG', 'SMEG'), ('SMEGP', 'SMEG+ / SMEG+ IV1'), ('SMEGP2', 'SMEG+ IV2'), ('NG4', 'NG4'), ('RNEG', 'RNEG'), ('NAC1', 'NAC wave1'), ('NAC2', 'NAC wave2'), ('NAC3', 'NAC wave3'), ('NAC4', 'NAC wave4')], max_length=20, verbose_name='modèle'),
        ),
    ]
