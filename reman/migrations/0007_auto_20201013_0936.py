# Generated by Django 3.1.2 on 2020-10-13 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reman', '0006_repair_psa_barcode'),
    ]

    operations = [
        migrations.AddField(
            model_name='ecurefbase',
            name='cal_ktag',
            field=models.CharField(blank=True, max_length=10, verbose_name='CAL_KTAG'),
        ),
        migrations.AddField(
            model_name='ecurefbase',
            name='open_diag',
            field=models.CharField(blank=True, max_length=16, verbose_name='OPENDIAG'),
        ),
        migrations.AddField(
            model_name='ecurefbase',
            name='ref_cal_out',
            field=models.CharField(blank=True, max_length=10, verbose_name='REF_CAL_OUT'),
        ),
        migrations.AddField(
            model_name='ecurefbase',
            name='ref_comp',
            field=models.CharField(blank=True, max_length=10, verbose_name='REF_COMP'),
        ),
        migrations.AddField(
            model_name='ecurefbase',
            name='ref_mat',
            field=models.CharField(blank=True, max_length=10, verbose_name='REF_MAT'),
        ),
        migrations.AddField(
            model_name='ecurefbase',
            name='ref_psa_out',
            field=models.CharField(blank=True, max_length=10, verbose_name='REF_PSA_OUT'),
        ),
        migrations.AddField(
            model_name='ecurefbase',
            name='status',
            field=models.CharField(blank=True, max_length=16, verbose_name='STATUT'),
        ),
    ]
