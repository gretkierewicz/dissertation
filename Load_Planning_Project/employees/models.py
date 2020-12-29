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
    SEMESTER_CHOICES = [
        ('Winter', 'Winter'),
        ('Summer', 'Summer'),
    ]

    EXAM_TYPE_CHOICES = [
        ('None', 'No exam'),
        ('Oral', 'Oral'),
        ('Written', 'Written'),
    ]

    code = models.CharField(max_length=45, unique=True)
    name = models.CharField(max_length=45)
    supervisor = models.ForeignKey(Employees, on_delete=models.SET_NULL, null=True, related_name='modules')
    is_contact_type = models.BooleanField(default=False)
    semester = models.CharField(max_length=6, choices=SEMESTER_CHOICES, default='Winter')
    exam_type = models.CharField(max_length=7, choices=EXAM_TYPE_CHOICES, default='None')

    def __str__(self):
        return self.code


class Orders(models.Model):
    class Meta:
        unique_together = (('module', 'lesson_type'), )

    LESSON_TYPE_CHOICES = [
        ('Lecture', 'Lecture'),
        ('Laboratory', 'Laboratory'),
        ('Classes', 'Classes'),
        ('Project', 'Project'),
        ('Seminar', 'Seminar'),
    ]

    module = models.ForeignKey(Modules, on_delete=models.CASCADE, related_name='orders')
    lesson_type = models.CharField(max_length=10, choices=LESSON_TYPE_CHOICES, default='Lecture')
    hours = models.PositiveIntegerField()

    def __str__(self):
        return '{}_{}'.format(self.module, self.lesson_type)
