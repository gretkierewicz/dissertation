from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from AGH.data.Classes_names import CLASSES_NAMES
from schedules.models import Schedules


class Modules(models.Model):
    class Meta:
        ordering = ['module_code']
        unique_together = (('module_code', 'schedule'),)

    module_code = models.SlugField(max_length=45)
    name = models.CharField(max_length=256)
    examination = models.BooleanField(default=False)
    schedule = models.ForeignKey(Schedules, on_delete=models.CASCADE, related_name='modules')
    language = models.CharField(max_length=2, default='pl')

    def __str__(self):
        return f'{self.module_code}' + (f' (name: {self.name})' if self.name else '') + f' module of {self.schedule}'

    def __repr__(self):
        return self.module_code

    @property
    def main_order(self):
        try:
            classes = self.form_of_classes.exclude(order=None).get(name='Lectures')
        except ObjectDoesNotExist:
            classes = self.form_of_classes.exclude(order=None).first()
        return classes.order if classes else None

    @property
    def exams_portion_staffed(self):
        return sum([x.portion for x in self.exams_additional_hours.all()])

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
        return f'{self.name} of {self.module}'
