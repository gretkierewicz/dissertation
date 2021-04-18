from django.db import models

from AGH.data.Classes_names import CLASSES_NAMES
from employees.models import Employees
from schedules.models import Schedules


class Modules(models.Model):
    class Meta:
        ordering = ['module_code']
        unique_together = (('module_code', 'schedule'),)

    module_code = models.SlugField(max_length=45)
    name = models.CharField(max_length=256)
    examination = models.BooleanField(default=False)
    supervisor = models.ForeignKey(Employees, on_delete=models.SET_NULL, null=True, related_name='supervised_modules')
    schedule = models.ForeignKey(Schedules, on_delete=models.CASCADE, related_name='modules')

    def __str__(self):
        return f"{self.name} (Code: {self.module_code})"

    def __repr__(self):
        return self.module_code

    @property
    def lectures_hours(self):
        return self.__return_classes_hours(name='Lectures')

    @property
    def laboratory_classes_hours(self):
        return self.__return_classes_hours(name='Laboratory_classes')

    @property
    def auditorium_classes_hours(self):
        return self.__return_classes_hours(name='Auditorium_classes')

    @property
    def project_classes_hours(self):
        return self.__return_classes_hours(name='Project_classes')

    @property
    def seminar_classes_hours(self):
        return self.__return_classes_hours(name='Seminar_classes')

    def __return_classes_hours(self, name):
        if name in [slug for slug, _ in Classes.NAME_CHOICES]:
            classes = self.classes.filter(name=name).first()
            return classes.classes_hours if classes else 0
        return None


class Classes(models.Model):
    class Meta:
        ordering = ['module', 'name']
        unique_together = (('module', 'name'),)

    NAME_CHOICES = [(_, _) for _ in CLASSES_NAMES]

    module = models.ForeignKey(Modules, on_delete=models.CASCADE, related_name='form_of_classes')
    name = models.CharField(max_length=31, choices=NAME_CHOICES, default=CLASSES_NAMES[0])
    classes_hours = models.PositiveIntegerField()
    students_limit_per_group = models.PositiveIntegerField(null=True)

    def __str__(self):
        return f"{self.module.module_code} ({self.module.name}): {self.name}"

    def __repr__(self):
        return f"{self.module.module_code}: {self.name}"
