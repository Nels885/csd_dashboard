# Generated by Django 3.2.18 on 2023-03-29 09:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('psa', '0004_suppliercode'),
    ]

    operations = [
        migrations.AddField(
            model_name='corvetproduct',
            name='dmtx',
            field=models.ForeignKey(blank=True, limit_choices_to={'type': 'DMTX'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='corvet_dmtx', to='psa.ecu'),
        ),
        migrations.AlterField(
            model_name='ecu',
            name='type',
            field=models.CharField(choices=[('BSI', 'Boitier Servitude Intelligent'), ('BSM', 'Boitier Servitude Moteur'), ('CMB', 'Combine Planche de Bord'), ('CMM', 'Calculateur Moteur Multifonction'), ('EMF', 'Ecran Multifonctions'), ('FMUX', 'Façade Multiplexée'), ('HDC', 'Haut de Colonne de Direction (COM200x)'), ('MDS', 'Module de service telematique'), ('CVM2', 'Camera Video Multifonction V2'), ('VMF', 'Module Commutation Integre'), ('DMTX', 'Dispositif Maintien Tension')], max_length=7, verbose_name='type'),
        ),
    ]