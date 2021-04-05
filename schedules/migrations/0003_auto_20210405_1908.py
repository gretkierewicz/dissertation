# Generated by Django 3.1.3 on 2021-04-05 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0002_pensum_pensumfactors'),
    ]

    operations = [
        migrations.AddField(
            model_name='pensum',
            name='value',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='pensumfactors',
            name='addition_value',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='pensumfactors',
            name='multiplication_value',
            field=models.FloatField(default=1),
        ),
    ]
