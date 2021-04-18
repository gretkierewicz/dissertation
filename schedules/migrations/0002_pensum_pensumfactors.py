# Generated by Django 3.1.3 on 2021-04-05 16:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('employees', '0003_remove_employees_pensum_value'),
        ('schedules', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pensum',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('basic_threshold', models.FloatField(default=0)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pensums',
                                               to='employees.employees')),
                ('schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pensums',
                                               to='schedules.schedules')),
            ],
            options={
                'unique_together': {('schedule', 'employee')},
            },
        ),
        migrations.CreateModel(
            name='PensumFactors',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('multiplication_value', models.FloatField()),
                ('addition_value', models.FloatField()),
                ('pensum', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='factors',
                                             to='schedules.pensum')),
            ],
        ),
    ]
