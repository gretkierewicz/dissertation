# Generated by Django 3.1.3 on 2021-04-23 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0003_remove_employees_pensum_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='employees',
            name='pensum_group',
            field=models.CharField(choices=[('dydaktyczna', 'dydaktyczna'), ('badawczo-dydaktyczna', 'badawczo-dydaktyczna')], default='dydaktyczna', max_length=20),
        ),
    ]