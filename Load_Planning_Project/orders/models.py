from math import ceil

from django.db import models

from employees.models import Employees
from modules.models import Classes


class Orders(models.Model):
    classes = models.OneToOneField(Classes, on_delete=models.CASCADE)
    students_number = models.PositiveIntegerField()
    order_number = models.CharField(max_length=50, blank=True, null=True)

    @property
    def groups_number(self):
        if self.classes.students_limit_per_group:
            return ceil(self.students_number / self.classes.students_limit_per_group)
        else:
            return 1

    @property
    def order_hours(self):
        return self.groups_number * self.classes.classes_hours

    def __str__(self):
        return f"Order of: {self.classes}"


class Plans(models.Model):
    class Meta:
        unique_together = ['classes', 'employee']

    classes = models.ForeignKey(Classes, on_delete=models.CASCADE, related_name='plans')
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name='plans')
    plan_hours = models.PositiveIntegerField()
