# Generated by Django 3.2.13 on 2022-04-26 09:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0021_auto_20220412_1302'),
    ]

    operations = [
        migrations.CreateModel(
            name='SuptechFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='suptech/%Y/%m')),
                ('suptech', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tools.suptech')),
            ],
            options={
                'verbose_name': 'Suptech File',
            },
        ),
    ]