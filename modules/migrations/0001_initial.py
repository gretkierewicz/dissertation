# Generated by Django 3.1.3 on 2021-02-21 20:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('employees', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Modules',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('module_code', models.SlugField(max_length=45, unique=True)),
                ('name', models.CharField(max_length=45)),
                ('examination', models.BooleanField(default=False)),
                ('supervisor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='supervised_modules', to='employees.employees')),
            ],
            options={
                'ordering': ['module_code'],
            },
        ),
        migrations.CreateModel(
            name='Classes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('Lectures', 'Lectures'), ('Laboratory classes', 'Laboratory classes'), ('Auditorium classes', 'Auditorium classes'), ('Project classes', 'Project classes'), ('Seminar classes', 'Seminar classes')], default='Lectures', max_length=18)),
                ('classes_hours', models.PositiveIntegerField()),
                ('students_limit_per_group', models.PositiveIntegerField(null=True)),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classes', to='modules.modules')),
            ],
            options={
                'ordering': ['module', 'name'],
                'unique_together': {('module', 'name')},
            },
        ),
    ]