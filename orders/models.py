from math import ceil

from django.db import models

from AGH.AGH_utils import get_major_factors_value
from employees.models import Employees
from modules.models import Classes


class Orders(models.Model):
    classes = models.OneToOneField(Classes, on_delete=models.CASCADE, related_name='order', primary_key=True)
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

    @property
    def plans_sum_hours(self):
        return sum([_.plan_hours for _ in self.plans.all()])

    def __str__(self):
        return f"Order of {self.classes}"


def get_plans_additional_hours(module, plan_hours):
    # TODO: consider using filter if list of congress lang. is given
    factor = get_major_factors_value('congress language factor')
    return 0 if module.language == 'pl' else plan_hours * factor


class Plans(models.Model):
    class Meta:
        unique_together = ['order', 'employee']

    order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name='plans')
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name='plans')
    plan_hours = models.PositiveIntegerField()

    @property
    def plan_additional_hours(self):
        return get_plans_additional_hours(self.order.classes.module, self.plan_hours)

    def __str__(self):
        return f"{self.employee}'s plan of {self.order.classes}"
