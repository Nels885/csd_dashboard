# Generated by Django 3.1.2 on 2020-11-18 15:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reman', '0007_auto_20201013_0936'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ecumodel',
            name='ecu_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='reman.ecutype'),
        ),
        migrations.AlterField(
            model_name='ecurefbase',
            name='ecu_type',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ecu_ref_base', to='reman.ecutype'),
        ),
        migrations.AlterField(
            model_name='ecutype',
            name='spare_part',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='reman.sparepart'),
        ),
        migrations.AlterField(
            model_name='repair',
            name='default',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='repairs', to='reman.default'),
        ),
        migrations.AlterField(
            model_name='repair',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='repairs_modified', to=settings.AUTH_USER_MODEL),
        ),
    ]