from django.db import models

from AGH.AGH_utils import badawczo_dydaktyczna, dydaktyczna


class Degrees(models.Model):
    class Meta:
        ordering = ['name']

    name = models.CharField(max_length=45, unique=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class Positions(models.Model):
    class Meta:
        ordering = ['name']

    name = models.CharField(max_length=45, unique=True)

    def __str__(self):
        return self.name

    def __repr__(self):
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
    supervisor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='subordinates')
    year_of_studies = models.PositiveSmallIntegerField(null=True, blank=True)
    is_procedure_for_a_doctoral_degree_approved = models.BooleanField(default=False)
    has_scholarship = models.BooleanField(default=False)
    pensum_group = models.CharField(
        max_length=max([len(gr) for gr in (badawczo_dydaktyczna, dydaktyczna)]),
        choices=PENSUM_GROUPS_CHOICES,
        default=dydaktyczna
    )

    def __str__(self):
        return self.abbreviation

    def __repr__(self):
        return self.abbreviation
