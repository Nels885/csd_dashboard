# Generated by Django 3.2.18 on 2023-04-19 08:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='suptechcategory',
            name='cc',
            field=models.TextField(default='test1@test.com; test2@test.com', max_length=5000, verbose_name='CC'),
        ),
        migrations.AddField(
            model_name='suptechcategory',
            name='to',
            field=models.TextField(default='test1@test.com; test2@test.com', max_length=5000, verbose_name='TO'),
        ),
        migrations.AlterField(
            model_name='suptechmessage',
            name='added_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='ajouté le'),
        ),
    ]