# Generated by Django 2.2.2 on 2019-06-11 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('squalaetp', '0001_initial'),
        ('raspeedi', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='raspeedi',
            name='corvets',
            field=models.ManyToManyField(blank=True, related_name='raspeedi', to='squalaetp.Corvet'),
        ),
    ]
