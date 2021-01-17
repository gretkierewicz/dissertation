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

    # simple method to count hours included in classes' plans
    def get_set_hours(self):
        return sum([plan.plan_hours for plan in self.plan.all()])

    # simple method to count hours not included in classes' plans
    def get_unset_hours(self):
        return self.classes_hours - self.get_set_hours()


class Plans(models.Model):
    class Meta:
        unique_together = (('employee', 'classes'), )

    employee = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name='plan')
    classes = models.ForeignKey(Classes, on_delete=models.CASCADE, related_name='plan')
    plan_hours = models.PositiveIntegerField()