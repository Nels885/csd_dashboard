# Generated by Django 3.2.22 on 2023-11-06 10:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('psa', '0012_auto_20230925_1403'),
    ]

    operations = [
        migrations.AddField(
            model_name='corvetproduct',
            name='bpga',
            field=models.ForeignKey(blank=True, limit_choices_to={'type': 'BPGA'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='corvet_bpga', to='psa.ecu'),
        ),
        migrations.AlterField(
            model_name='ecu',
            name='type',
            field=models.CharField(choices=[('BSI', 'Boitier Servitude Intelligent'), ('BSM', 'Boitier Servitude Moteur'), ('CMB', 'Combine Planche de Bord'), ('CMM', 'Calculateur Moteur Multifonction'), ('EMF', 'Ecran Multifonctions'), ('FMUX', 'Façade Multiplexée'), ('HDC', 'Haut de Colonne de Direction (COM200x)'), ('MDS', 'Module de service telematique'), ('CVM2', 'Camera Video Multifonction V2'), ('VMF', 'Module Commutation Integre'), ('DMTX', 'Dispositif Maintien Tension'), ('BPGA', 'Boitier Protection Alimentation Reseau Elec')], max_length=10, verbose_name='type'),
        ),
    ]
