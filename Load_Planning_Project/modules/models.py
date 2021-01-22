from django.db import models

from employees.models import Employees


class Modules(models.Model):
    class Meta:
        ordering = ['module_code']

    module_code = models.SlugField(max_length=45, unique=True)
    name = models.CharField(max_length=45)
    examination = models.BooleanField(default=False)
    supervisor = models.ForeignKey(Employees, on_delete=models.SET_NULL, null=True, related_name='supervised_modules')

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
        ordering = ['name']
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
        return f"{self.name} of {self.module.module_code}"

    @property
    # classes' already set hours
    def classes_hours_set(self):
        return sum([plan.plan_hours for plan in self.plans.all()])

    @property
    # classes' hours waiting to be set
    def classes_hours_not_set(self):
        return self.classes_hours - self.classes_hours_set

    @property
    # True/False for filling all classes' hours with it's plans' hours
    def is_class_full(self):
        return self.classes_hours_not_set <= 0


class Plans(models.Model):
    class Meta:
        ordering = ['employee', 'classes']
        unique_together = (('employee', 'classes'), )

    employee = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name='plans')
    classes = models.ForeignKey(Classes, on_delete=models.CASCADE, related_name='plans')
    plan_hours = models.PositiveIntegerField()
