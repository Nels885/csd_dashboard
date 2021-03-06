# Generated by Django 3.2 on 2021-04-13 11:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('psa', '0015_alter_corvetchoices_column'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ecu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comp_ref', models.CharField(max_length=10, unique=True, verbose_name='réf. comp. matériel')),
                ('mat_ref', models.CharField(blank=True, max_length=10, verbose_name='réf. matériel')),
                ('name', models.CharField(max_length=50, verbose_name='nom du modèle')),
                ('type', models.CharField(choices=[('BSI', 'Boitier Servitude Intelligent'), ('EMF', 'Ecran Multifonctions'), ('MDS', 'Module de service telematique'), ('CMM', 'Calculateur Moteur Multifonction'), ('BSM', 'Boitier Servitude Moteur'), ('HDC', 'Haut de Colonne de Direction (COM200x)')], max_length=3, verbose_name='type')),
                ('first_barcode', models.CharField(blank=True, max_length=200, verbose_name='premier code-barres')),
                ('second_barcode', models.CharField(blank=True, max_length=200, verbose_name='deuxième code-barres')),
                ('hw', models.CharField(blank=True, max_length=10, verbose_name='HW')),
                ('sw', models.CharField(blank=True, max_length=10, verbose_name='SW')),
                ('supplier_oe', models.CharField(blank=True, max_length=50, verbose_name='fabriquant')),
                ('pr_reference', models.CharField(blank=True, max_length=10, verbose_name='référence PR')),
                ('extra', models.CharField(blank=True, max_length=100, verbose_name='supplément')),
            ],
            options={
                'verbose_name': 'Données ECU',
                'ordering': ['comp_ref'],
            },
        ),
        migrations.AddField(
            model_name='corvet',
            name='bsm',
            field=models.ForeignKey(blank=True, limit_choices_to={'type': 'BSM'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='corvet_bsm', to='psa.ecu'),
        ),
        migrations.AddField(
            model_name='corvet',
            name='cmm',
            field=models.ForeignKey(blank=True, limit_choices_to={'type': 'CMM'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='corvet_cmm', to='psa.ecu'),
        ),
        migrations.AlterField(
            model_name='corvet',
            name='bsi',
            field=models.ForeignKey(blank=True, limit_choices_to={'type': 'BSI'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='corvet_bsi', to='psa.ecu'),
        ),
        migrations.DeleteModel(
            name='BsiModel',
        ),
    ]
