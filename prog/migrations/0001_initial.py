# Generated by Django 3.2.16 on 2023-02-08 13:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('psa', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('squalaetp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Raspeedi',
            fields=[
                ('ref_boitier', models.BigIntegerField(primary_key=True, serialize=False, verbose_name='référence boîtier')),
                ('produit', models.CharField(choices=[('RT4', 'RT4'), ('RT5', 'RT5'), ('RT6', 'RT6'), ('RT6v2', 'RT6 version 2'), ('SMEG', 'SMEG'), ('SMEGP', 'SMEG+ / SMEG+ IV1'), ('SMEGP2', 'SMEG+ IV2')], max_length=20, verbose_name='produit')),
                ('facade', models.CharField(max_length=2, verbose_name='façade')),
                ('type', models.CharField(choices=[('RAD', 'Radio'), ('NAV', 'Navigation')], max_length=3, verbose_name='type')),
                ('dab', models.BooleanField(default=False, verbose_name='DAB')),
                ('cam', models.BooleanField(default=False, verbose_name='caméra de recul')),
                ('dump_peedi', models.CharField(blank=True, max_length=25, verbose_name='dump PEEDI')),
                ('cd_version', models.CharField(blank=True, max_length=10, verbose_name='version CD')),
                ('media', models.CharField(blank=True, choices=[('N/A', 'Vide'), ('HDD', 'Disque Dur'), ('8Go', 'Carte SD 8Go'), ('16Go', 'Carte SD 16Go'), ('8Go 16Go', 'Carte SD 8 ou 16 Go')], max_length=20, verbose_name='type de média')),
                ('carto', models.CharField(blank=True, max_length=20, verbose_name='version cartographie')),
                ('dump_renesas', models.CharField(blank=True, max_length=50, verbose_name='dump RENESAS')),
                ('ref_mm', models.CharField(blank=True, max_length=200, verbose_name='référence MM')),
                ('connecteur_ecran', models.IntegerField(blank=True, choices=[(1, '1'), (2, '2')], null=True, verbose_name="nombre de connecteur d'écran")),
            ],
            options={
                'verbose_name': 'Données RASPEEDI',
                'ordering': ['ref_boitier'],
            },
        ),
        migrations.CreateModel(
            name='UnlockProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='ajouté le')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='modifié le')),
                ('unlock', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='squalaetp.xelon')),
                ('user', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Déverrouillage VIN',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Programing',
            fields=[
                ('psa_barcode', models.BigIntegerField(primary_key=True, serialize=False, verbose_name='référence boîtier')),
                ('peedi_path', models.CharField(max_length=20, verbose_name='dossier PEEDI')),
                ('peedi_dump', models.CharField(blank=True, max_length=25, verbose_name='dump PEEDI')),
                ('renesas_dump', models.CharField(blank=True, max_length=50, verbose_name='dump RENESAS')),
                ('multimedia', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='prog', to='psa.multimedia')),
            ],
            options={
                'verbose_name': 'Données Programmation',
                'ordering': ['psa_barcode'],
            },
        ),
        migrations.CreateModel(
            name='AddReference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('add_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='prog.raspeedi')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]