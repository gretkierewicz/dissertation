# Generated by Django 3.1.3 on 2021-05-16 20:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('modules', '0010_auto_20210426_2033'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='modules',
            name='supervisor',
        ),
    ]
