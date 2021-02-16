from django.db import models

from utils.constants import GT, ET, LT, NA


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
        (GT, GT),
        (ET, ET),
        (LT, LT),
        (NA, NA)
    ]
    DOCTORAL_PROCEDURE_CHOICES = [
        ('True', 'YES'),
        (NA, NA),
        ('False', 'NO')
    ]
    SCHOLARSHIP_CHOICES = [
        ('True', 'YES'),
        (NA, NA),
        ('False', 'NO')
    ]

    name = models.CharField(max_length=100, unique=True)
    value = models.PositiveIntegerField()
    limit = models.PositiveIntegerField(default=0, null=True)
    degrees = models.ManyToManyField(Degrees, related_name='pensum')
    positions = models.ManyToManyField(Positions, related_name='pensum', blank=True)
    year_of_studies = models.PositiveSmallIntegerField(null=True, blank=True)
    year_condition = models.CharField(max_length=12, choices=YEAR_CONDITION_CHOICES, default=NA)
    is_procedure_for_a_doctoral_degree_approved = models.CharField(max_length=5, choices=DOCTORAL_PROCEDURE_CHOICES,
                                                                   default=NA)
    has_scholarship = models.CharField(max_length=5, choices=SCHOLARSHIP_CHOICES, default=NA)

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
        return self.abbreviation

    def __repr__(self):
        return self.abbreviation

    @property
    # find pensum instance that corresponds to employee's data
    # TODO: consider creating table that will keep employee-pensum relations (updated on save of employee or pensum)
    def pensum(self):
        query = Pensum.objects.filter(
            degrees=self.degree,
            positions=self.position,
            is_procedure_for_a_doctoral_degree_approved__in=[NA, self.is_procedure_for_a_doctoral_degree_approved],
            has_scholarship__in=[NA, self.has_scholarship]
        )
        for pensum in query:
            if (pensum.year_condition == NA) or \
                    (pensum.year_condition == GT and self.year_of_studies > pensum.year_of_studies) or \
                    (pensum.year_condition == ET and self.year_of_studies == pensum.year_of_studies) or \
                    (pensum.year_condition == LT and self.year_of_studies < pensum.year_of_studies):
                return pensum
        return None

    @property
    # get pensum's name
    def pensum_name(self):
        return self.pensum.name

    @property
    # pensum value from Employee's instance degree and position
    def pensum_value(self):
        pensum = self.pensum
        return pensum.value if pensum else 0

    @property
    # pensum limit from Employee's instance degree and position
    def pensum_limit(self):
        pensum = self.pensum
        return pensum.limit if pensum else 0
