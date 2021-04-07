from django.db import models

from AGH.AGH_utils import get_pensum_function_names, get_pensum_reduction_value
from employees.models import Employees


class Schedules(models.Model):
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.slug


class Pensum(models.Model):
    class Meta:
        unique_together = (('schedule', 'employee'), )

    schedule = models.ForeignKey(Schedules, on_delete=models.CASCADE, related_name='pensums')
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name='pensums')
    basic_threshold = models.FloatField(default=0)

    @property
    def calculated_threshold(self):
        # TODO: check if reduction should be calculated at first
        ret = self.basic_threshold
        for function in self.reductions.all():
            ret -= function.reduction_value
        # pass factors if reduction zeros calculated threshold
        if ret < 0:
            return 0

        for factor in self.factors.all():
            ret = factor.calculate_value(ret)
        return ret

    @property
    def planned_pensum_hours(self):
        return sum([plan.plan_hours for plan in self.employee.plans.all()])


class PensumFactors(models.Model):
    ADD = 'Addition'
    MUL = 'Multiplication'
    TYPES = [
        (ADD, ADD),
        (MUL, MUL),
    ]

    pensum = models.ForeignKey(Pensum, on_delete=models.CASCADE, related_name='factors')
    name = models.CharField(max_length=64, default='')
    factor_type = models.CharField(max_length=len(MUL), choices=TYPES, default=ADD)
    value = models.FloatField(default=1)

    def calculate_value(self, value):
        if self.factor_type == self.ADD:
            return value + self.value
        if self.factor_type == self.MUL:
            return value * self.value


class PensumReductions(models.Model):
    class Meta:
        unique_together = (('pensum', 'function'), )

    ROLES = [(name, name) for name in get_pensum_function_names()]

    pensum = models.ForeignKey(Pensum, on_delete=models.CASCADE, related_name='reductions')
    function = models.CharField(max_length=max([len(name) for name in get_pensum_function_names()]), choices=ROLES)

    @property
    def reduction_value(self):
        return get_pensum_reduction_value(self.function)
