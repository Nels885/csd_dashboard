# Generated by Django 3.1.1 on 2020-09-16 16:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('squalaetp', '0017_auto_20200505_1130'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='code Produit')),
            ],
        ),
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code_magasin', models.CharField(blank=True, max_length=20, verbose_name='code Magasin')),
                ('code_zone', models.CharField(blank=True, max_length=20, verbose_name='code Zone')),
                ('code_site', models.IntegerField(blank=True, null=True, verbose_name='code Site')),
                ('code_emplacement', models.CharField(blank=True, max_length=10, verbose_name='code Emplacement')),
                ('cumul_dispo', models.IntegerField(blank=True, null=True, verbose_name='cumul Dispo')),
                ('code_produit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='squalaetp.productcode')),
            ],
        ),
    ]
