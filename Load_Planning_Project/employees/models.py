from django.db import models


class Degrees(models.Model):
    name = models.CharField(max_length=45, unique=True)

    def __str__(self):
        return self.name


class Positions(models.Model):
    name = models.CharField(max_length=45, unique=True)

    def __str__(self):
        return self.name


class Employees(models.Model):
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    abbreviation = models.CharField(max_length=5, unique=True)
    degree = models.ForeignKey(Degrees, on_delete=models.SET_NULL, null=True, related_name='employees')
    position = models.ForeignKey(Positions, on_delete=models.SET_NULL, null=True, related_name='employees')
    e_mail = models.EmailField(max_length=45, unique=True)
    supervisor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='subordinates')
    year_of_studies = models.PositiveSmallIntegerField(null=True, blank=True)
    is_procedure_for_a_doctoral_degree_approved = models.BooleanField(default=False)
    has_scholarship = models.BooleanField(default=False)

    def __str__(self):
        return self.abbreviation


class Modules(models.Model):
    EXAM_TYPE_CHOICES = [
        ('n', 'no exam'),
        ('o', 'oral'),
        ('w', 'written'),
    ]

    SEMESTER_CHOICES = [
        ('w', 'winter'),
        ('s', 'summer'),
    ]

    code = models.CharField(max_length=45, unique=True)
    name = models.CharField(max_length=45)
    supervisor = models.ForeignKey(Employees, on_delete=models.SET_NULL, null=True, related_name='modules')
    is_contact_type = models.BooleanField(default=False)
    semester = models.CharField(max_length=1, choices=SEMESTER_CHOICES, default='w')
    exam_type = models.CharField(max_length=1, choices=EXAM_TYPE_CHOICES, default='n')

    def __str__(self):
        return self.code
