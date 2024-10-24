# Generated by Django 3.2.22 on 2023-11-06 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('squalaetp', '0003_alter_productcategory_corvet_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productcategory',
            name='corvet_type',
            field=models.CharField(blank=True, choices=[('RAD', 'Radio'), ('NAV', 'Navigation'), ('BSI', 'Boitier Servitude Intelligent'), ('BSM', 'Boitier Servitude Moteur'), ('CMB', 'Combine Planche de Bord'), ('CMM', 'Calculateur Moteur Multifonction'), ('EMF', 'Ecran Multifonctions'), ('FMUX', 'Façade Multiplexée'), ('HDC', 'Haut de Colonne de Direction (COM200x)'), ('MDS', 'Module de service telematique'), ('CVM2', 'Camera Video Multifonction V2'), ('VMF', 'Module Commutation Integre'), ('DMTX', 'Dispositif Maintien Tension'), ('BPGA', 'Boitier Protection Alimentation Reseau Elec')], max_length=50, verbose_name='Type Corvet'),
        ),
    ]
