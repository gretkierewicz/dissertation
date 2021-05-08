from django.db import models

from AGH.AGH_utils import (
    AdditionalHoursFactorData,
    ExamsFactors,
    get_additional_hours_factors_choices,
    get_exam_hours,
    get_major_factors_value,
    get_job_time_hours_limit,
    get_pensum_function_names,
    get_pensum_reduction_value
)
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
    def pensum_additional_hours_not_counted_into_limit(self):
        return sum([
            factor.total_factor_hours for factor in self.additional_hours_factors.all()
            if not AdditionalHoursFactorData(factor.name).is_counted_into_limit
        ])

    @property
    def pensum_additional_hours(self):
        sum_of_factors_hours = sum([factor.total_factor_hours for factor in self.additional_hours_factors.all()])
        # add additional hours for plans with congress language
        sum_of_factors_hours += sum([plan.plan_additional_hours for plan in self.employee.plans.all()])
        # examination additional hours
        exam_additional_hours = sum([exam.total_factor_hours for exam in self.exams_additional_hours.all()])
        return (sum_of_factors_hours + min(exam_additional_hours, ExamsFactors.max_summary_hours)).__round__(2)

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

    @property
    def min_for_contact_hours(self):
        relative_min = 1 - get_major_factors_value("max relative deficit for contact hours")
        absolute_min = self.calculated_threshold - get_major_factors_value("max absolute deficit for contact hours")
        return max([relative_min * self.calculated_threshold, absolute_min])

    @property
    def amount_until_contact_hours_min(self):
        hours = self.min_for_contact_hours - self.pensum_contact_hours
        return hours if hours >= 0 else 0

    @property
    def limit_for_contact_hours(self):
        ret = self.calculated_threshold
        if self.employee.part_of_job_time < 1.0:
            ret *= get_job_time_hours_limit("part-job contact hours limit")
        else:
            ret *= get_job_time_hours_limit("full-job contact hours limit")
        return ret

    @property
    def amount_until_contact_hours_limit(self):
        return min(self.limit_for_contact_hours - self.pensum_contact_hours , self.amount_until_over_time_hours_limit)

    @property
    def limit_for_over_time_hours(self):
        return self.calculated_threshold * get_job_time_hours_limit("over-time hours limit")

    @property
    def amount_until_over_time_hours_limit(self):
        return (self.limit_for_over_time_hours - self.pensum_contact_hours - self.pensum_additional_hours
                + self.pensum_additional_hours_not_counted_into_limit).__round__(2)


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

    @property
    def total_factor_hours(self):
        return self.value_per_unit * self.amount

    @property
    def total_factor_hours_counted_into_limit(self):
        return self.total_factor_hours if AdditionalHoursFactorData(self.name).is_counted_into_limit else 0


class ExamsAdditionalHours(models.Model):
    class Meta:
        unique_together = (('pensum', 'module'),)

    EXAM_TYPES_CHOICES = [
        ('Written', "Written"),
        ('Oral', 'Oral')
    ]
    from modules.models import Modules

    pensum = models.ForeignKey(Pensum, on_delete=models.CASCADE, related_name='exams_additional_hours')
    module = models.ForeignKey(Modules, on_delete=models.CASCADE, related_name='exams_additional_hours')
    type = models.CharField(max_length=8, choices=EXAM_TYPES_CHOICES, default=EXAM_TYPES_CHOICES[0][0])
    portion = models.FloatField(default=1)

    @property
    def total_factor_hours(self):
        if not self.module.main_order:
            return 0
        if self.module.main_order.students_number > ExamsFactors.min_students_number:
            return self.portion * get_exam_hours(self.module, self.type)
