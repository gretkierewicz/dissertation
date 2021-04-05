from django.db import models


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

    def __str__(self):
        return self.abbreviation

    def __repr__(self):
        return self.abbreviation
