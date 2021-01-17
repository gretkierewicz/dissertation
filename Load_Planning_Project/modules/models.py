from django.db import models

from employees.models import Employees


class Modules(models.Model):
    module_code = models.SlugField(max_length=45, unique=True)
    name = models.CharField(max_length=45)
    examination = models.BooleanField(default=False)
    supervisor = models.ForeignKey(Employees, on_delete=models.SET_NULL, null=True, related_name='supervised_modules')

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

    module = models.ForeignKey(Modules, on_delete=models.CASCADE, related_name='classes')
    name = models.CharField(max_length=18, choices=NAME_CHOICES, default='Lectures')
    classes_hours = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    def __repr__(self):
        return "{class_name} (Module's code: {module})".format(module=self.module, class_name=self.name)

    # property to check classes' already set hours
    @property
    def classes_hours_set(self):
        return sum([plan.plan_hours for plan in self.plans.all()])

    # property to check classes' hour waiting to be set
    @property
    def classes_hours_not_set(self):
        return self.classes_hours - self.classes_hours_set


class Plans(models.Model):
    class Meta:
        unique_together = (('employee', 'classes'), )

    employee = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name='plans')
    classes = models.ForeignKey(Classes, on_delete=models.CASCADE, related_name='plans')
    plan_hours = models.PositiveIntegerField()
