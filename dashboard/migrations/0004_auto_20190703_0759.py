# Generated by Django 2.2.2 on 2019-07-03 05:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_auto_20190702_1357'),
    ]

    operations = [
        migrations.AlterField(
            model_name='csdsoftware',
            name='status',
            field=models.CharField(choices=[('Validé', 'Validé'), ('En test', 'En test'), ('Etudes', 'Etudes'), ('Abandonné', 'Abandonné'), ('PDI Only', 'PDI Only')], max_length=50),
        ),
    ]
