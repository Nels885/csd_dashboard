# Generated by Django 2.2.5 on 2019-09-16 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('raspeedi', '0006_auto_20190903_1755'),
    ]

    operations = [
        migrations.AlterField(
            model_name='raspeedi',
            name='carto',
            field=models.CharField(blank=True, max_length=20, verbose_name='version cartographie'),
        ),
        migrations.AlterField(
            model_name='raspeedi',
            name='cd_version',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AlterField(
            model_name='raspeedi',
            name='connecteur_ecran',
            field=models.IntegerField(blank=True, choices=[(1, '1'), (2, '2')], null=True, verbose_name="nombre de connecteur d'écran"),
        ),
        migrations.AlterField(
            model_name='raspeedi',
            name='dump_peedi',
            field=models.CharField(blank=True, max_length=25, verbose_name='dump PEEDI'),
        ),
        migrations.AlterField(
            model_name='raspeedi',
            name='dump_renesas',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='raspeedi',
            name='media',
            field=models.CharField(blank=True, choices=[('N/A', 'Vide'), ('HDD', 'Disque Dur'), ('8Go', 'Carte SD 8Go'), ('16Go', 'Carte SD 16Go'), ('8Go 16Go', 'Carte SD 8 ou 16 Go')], max_length=20, verbose_name='type de média'),
        ),
        migrations.AlterField(
            model_name='raspeedi',
            name='ref_mm',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
