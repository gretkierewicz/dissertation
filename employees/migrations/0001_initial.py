# Generated by Django 3.1.3 on 2021-06-23 19:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Degrees',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45, unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Positions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45, unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Employees',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=45)),
                ('last_name', models.CharField(max_length=45)),
                ('abbreviation', models.SlugField(max_length=5, unique=True)),
                ('e_mail', models.EmailField(max_length=45, unique=True)),
                ('pensum_group', models.CharField(choices=[('dydaktyczna', 'dydaktyczna'), ('badawczo-dydaktyczna', 'badawczo-dydaktyczna')], default='dydaktyczna', max_length=20)),
                ('part_of_job_time', models.FloatField(default=1)),
                ('degree', models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='employees', to='employees.degrees')),
                ('position', models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='employees', to='employees.positions')),
            ],
            options={
                'ordering': ['abbreviation'],
            },
        ),
    ]
