# Generated by Django 3.2.20 on 2023-09-15 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('psa', '0009_auto_20230831_1159'),
    ]

    operations = [
        migrations.AlterField(
            model_name='multimedia',
            name='lvds_con',
            field=models.IntegerField(blank=True, choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4')], null=True, verbose_name="nombre d'LVDS"),
        ),
        migrations.CreateModel(
            name='CanRemote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=20, verbose_name='label')),
                ('location', models.IntegerField(verbose_name='position')),
                ('type', models.CharField(max_length=10, verbose_name='Type commande')),
                ('vehicle', models.CharField(blank=True, max_length=50, verbose_name='véhicule')),
                ('brand', models.CharField(blank=True, max_length=50, verbose_name='fabriquant')),
                ('product', models.CharField(blank=True, max_length=50, verbose_name='produit')),
                ('can_id', models.CharField(max_length=20, verbose_name='can_id')),
                ('dlc', models.IntegerField(default=0, verbose_name='DLC')),
                ('data', models.CharField(max_length=500, verbose_name='data')),
                ('corvets', models.ManyToManyField(blank=True, to='psa.Corvet')),
            ],
            options={
                'verbose_name': 'Télécommande CAN',
                'ordering': ['location'],
            },
        ),
    ]