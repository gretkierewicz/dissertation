from django.db import models

import modules.models


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


class Pensum(models.Model):
    YEAR_CONDITION_CHOICES = [
        ('greater than', 'greater than'),
        ('equal to', 'equal to'),
        ('less than', 'less than'),
        ('N/A', 'N/A')
    ]
    DOCTORAL_PROCEDURE_CHOICES = [
        ('True', 'YES'),
        ('N/A', 'N/A'),
        ('False', 'NO')
    ]
    SCHOLARSHIP_CHOICES = [
        ('True', 'YES'),
        ('N/A', 'N/A'),
        ('False', 'NO')
    ]

    name = models.CharField(max_length=100, unique=True)
    value = models.PositiveIntegerField()
    limit = models.PositiveIntegerField(default=0, null=True)
    degrees = models.ManyToManyField(Degrees, related_name='pensum')
    positions = models.ManyToManyField(Positions, related_name='pensum', blank=True)
    year_of_studies = models.PositiveSmallIntegerField(null=True, blank=True)
    year_condition = models.CharField(max_length=12, choices=YEAR_CONDITION_CHOICES, default='N/A')
    is_procedure_for_a_doctoral_degree_approved = models.CharField(max_length=5, choices=DOCTORAL_PROCEDURE_CHOICES,
                                                                   default='N/A')
    has_scholarship = models.CharField(max_length=5, choices=SCHOLARSHIP_CHOICES, default='N/A')

    def __str__(self):
        return f"{self.name} (value: {self.value}, limit: {self.limit})"

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
        return f"{self.first_name} {self.last_name} ({self.abbreviation})"

    def __repr__(self):
        return self.abbreviation

    @property
    # gets only modules with plans included in it for Employee instance
    def plan_modules(self):
        return modules.models.Modules.objects.filter(classes__plans__in=self.plans.all()
                                                     ).distinct().order_by('module_code')

    @property
    # summary plan hours for Employee instance
    def plan_hours_sum(self):
        return sum([plan.plan_hours for plan in modules.models.Plans.objects.filter(employee=self)])

    @property
    # pensum value from Employee's instance degree and position
    def pensum_value(self):
        pensum = Pensum.objects.filter(degrees=self.degree, positions=self.position).first()
        return pensum.value if pensum else 0

    @property
    # True/False for reaching pensum value by Employee instance
    def is_pensum_value_reached(self):
        return self.plan_hours_sum >= self.pensum_value

    @property
    # pensum limit from Employee's instance degree and position
    def pensum_limit(self):
        pensum = Pensum.objects.filter(degrees=self.degree, positions=self.position).first()
        return pensum.limit if pensum else 0

    @property
    # True/False for reaching pensum limit by Employee instance
    def is_pensum_limit_reached(self):
        return self.plan_hours_sum >= self.pensum_limit
