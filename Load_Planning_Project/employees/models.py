from django.db import models


class Degrees(models.Model):
    name = models.CharField(max_length=45, unique=True)

    def __str__(self):
        return self.name


class Positions(models.Model):
    name = models.CharField(max_length=45, unique=True)

    def __str__(self):
        return self.name


class Pensum(models.Model):
    value = models.PositiveIntegerField()
    degrees = models.ManyToManyField(Degrees, null=True, related_name='pensum')
    positions = models.ManyToManyField(Positions, null=True, related_name='pensum')


class Employees(models.Model):
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    abbreviation = models.SlugField(max_length=5, unique=True)
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
    module_code = models.SlugField(max_length=45, unique=True)
    name = models.CharField(max_length=45)
    examination = models.BooleanField(default=False)
    supervisor = models.ForeignKey(Employees, on_delete=models.SET_NULL, null=True, related_name='modules')

    def __str__(self):
        return self.module_code


class Classes(models.Model):
    class Meta:
        unique_together = (('module', 'name'), )

    NAME_CHOICES = [
        ('Lectures', 'Lectures'),
        ('Laboratory_classes', 'Laboratory classes'),
        ('Auditorium_classes', 'Auditorium classes'),
        ('Project_classes', 'Project classes'),
        ('Seminar_classes', 'Seminar classes'),
    ]

    module = models.ForeignKey(Modules, on_delete=models.CASCADE, related_name='form_of_classes')
    name = models.CharField(max_length=18, choices=NAME_CHOICES, default='Lectures')
    classes_hours = models.PositiveIntegerField()

    def __str__(self):
        return '{}/{}'.format(self.module, self.name)
