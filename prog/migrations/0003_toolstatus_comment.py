# Generated by Django 3.2.18 on 2023-02-22 21:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prog', '0002_toolstatus'),
    ]

    operations = [
        migrations.AddField(
            model_name='toolstatus',
            name='comment',
            field=models.TextField(blank=True, verbose_name='Commentaire'),
        ),
    ]