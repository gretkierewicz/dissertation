# Generated by Django 3.1.3 on 2021-04-05 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0005_auto_20210405_1916'),
    ]

    operations = [
        migrations.AddField(
            model_name='pensumfactors',
            name='value',
            field=models.FloatField(default=1),
        ),
    ]
