from django.db import models

from AGH.AGH_utils import get_additional_hours_factors_choices, get_major_factors_value, get_pensum_function_names, \
    get_pensum_reduction_value
from employees.models import Employees


class Schedules(models.Model):
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.slug


class Pensum(models.Model):
    class Meta:
        unique_together = (('schedule', 'employee'),)

    schedule = models.ForeignKey(Schedules, on_delete=models.CASCADE, related_name='pensums')
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name='pensums')
    basic_threshold = models.FloatField(default=0)

    @property
    def pensum_contact_hours(self):
        return sum([plan.plan_hours for plan in self.employee.plans.all()])

    @property
    def pensum_additional_hours(self):
        sum_of_factors_hours = sum(
            [factor.amount * factor.value_per_unit for factor in self.additional_hours_factors.all()])
        # add additional hours for plans with congress language
        # TODO: consider using filter if list of congress lang. is given
        # congress_language_plans = self.employee.plans.filter(order__classes__module__language__in=['en', 'fr', ...])
        congress_language_plans = self.employee.plans.exclude(order__classes__module__language='pl')
        congress_language_factor = get_major_factors_value('congress language factor')
        sum_of_factors_hours += sum([plan.plan_hours * congress_language_factor for plan in congress_language_plans])
        # TODO: examination additional hours
        return sum_of_factors_hours

    @property
    def calculated_threshold(self):
        ret = self.basic_threshold

        # reduce if employee has part-time job
        ret *= self.employee.part_of_job_time

        # calculate all basic threshold factors
        for factor in self.basic_threshold_factors.all():
            ret = factor.calculate_value(ret)

        # reduce with function's value
        try:
            ret -= self.reduction.reduction_value
        except Exception:
            # if instance has no reduction set
            pass
        return ret if ret > 0 else 0


class PensumBasicThresholdFactors(models.Model):
    ADD = 'Addition'
    MUL = 'Multiplication'
    TYPES = [
        (ADD, ADD),
        (MUL, MUL),
    ]

    pensum = models.ForeignKey(Pensum, on_delete=models.CASCADE, related_name='basic_threshold_factors')
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
        unique_together = (('pensum', 'function'),)

    ROLES = [(name, name) for name in get_pensum_function_names()]

    pensum = models.OneToOneField(Pensum, on_delete=models.CASCADE, related_name='reduction')
    function = models.CharField(max_length=max([len(name) for name in get_pensum_function_names()]), choices=ROLES)

    @property
    def reduction_value(self):
        return get_pensum_reduction_value(self.function)


class PensumAdditionalHoursFactors(models.Model):
    ADDITIONAL_HOURS_CHOICES = get_additional_hours_factors_choices()

    pensum = models.ForeignKey(Pensum, on_delete=models.CASCADE, related_name='additional_hours_factors')
    name = models.CharField(max_length=64, choices=ADDITIONAL_HOURS_CHOICES, default=ADDITIONAL_HOURS_CHOICES[0][0])
    value_per_unit = models.PositiveIntegerField()
    amount = models.PositiveIntegerField(default=1)
    description = models.CharField(max_length=128, blank=True)
