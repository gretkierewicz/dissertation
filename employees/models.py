from django.db import models

from AGH.AGH_utils import badawczo_dydaktyczna, dydaktyczna


class Degrees(models.Model):
    class Meta:
        ordering = ['name']

    name = models.CharField(max_length=45, unique=True)

    def __str__(self):
        return self.name


class Positions(models.Model):
    class Meta:
        ordering = ['name']

    name = models.CharField(max_length=45, unique=True)

    def __str__(self):
        return self.name


class Employees(models.Model):
    class Meta:
        ordering = ['abbreviation']

    PENSUM_GROUPS_CHOICES = [
        (dydaktyczna, dydaktyczna),
        (badawczo_dydaktyczna, badawczo_dydaktyczna)
    ]

    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    abbreviation = models.SlugField(max_length=5, unique=True)
    degree = models.ForeignKey(Degrees, on_delete=models.SET_DEFAULT, default=1, related_name='employees')
    position = models.ForeignKey(Positions, on_delete=models.SET_DEFAULT, default=1, related_name='employees')
    e_mail = models.EmailField(max_length=45, unique=True)
    pensum_group = models.CharField(
        max_length=max([len(gr) for gr in (badawczo_dydaktyczna, dydaktyczna)]),
        choices=PENSUM_GROUPS_CHOICES,
        default=dydaktyczna
    )
    part_of_job_time = models.FloatField(default=1)

    def __str__(self):
        return f"{self.abbreviation}: {self.first_name} {self.last_name}"
