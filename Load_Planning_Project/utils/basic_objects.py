from django.core.exceptions import ObjectDoesNotExist

from employees.models import Degrees, Positions, Employees
from modules.models import Modules, Classes, Plans


def basic_degree(name='basic_degree'):
    try:
        return Degrees.objects.get(name=name)
    except ObjectDoesNotExist:
        return Degrees.objects.create(name=name)


def basic_position(name='basic_position'):
    try:
        return Positions.objects.get(name=name)
    except ObjectDoesNotExist:
        return Positions.objects.create(name=name)


def basic_supervisor(abbreviation='SUPER'):
    name = abbreviation + '_employee'
    try:
        return Employees.objects.get(abbreviation=abbreviation)
    except ObjectDoesNotExist:
        return Employees.objects.create(
            first_name=name + '_first_name',
            last_name=name + '_last_name',
            abbreviation=abbreviation,
            e_mail=name + '@basic.basic',
            degree=basic_degree(),
            position=basic_position())


def basic_employee(abbreviation='BASIC'):
    name = abbreviation + '_employee'
    try:
        return Employees.objects.get(abbreviation=abbreviation)
    except ObjectDoesNotExist:
        return Employees.objects.create(
            first_name=name + '_first_name',
            last_name=name + '_last_name',
            abbreviation=abbreviation,
            e_mail=name + '@basic.basic',
            degree=basic_degree(),
            position=basic_position(),
            supervisor=basic_supervisor())


def basic_module(name='basic_module'):
    try:
        return Modules.objects.get(module_code=name)
    except ObjectDoesNotExist:
        return Modules.objects.create(name=name, module_code=name)


def basic_classes(classes_hours=100, name=Classes.NAME_CHOICES[0][0]):
    try:
        return Classes.objects.get(module=basic_module(), name=name)
    except ObjectDoesNotExist:
        return Classes.objects.create(module=basic_module(), name=name, classes_hours=classes_hours)


def basic_plans(employee, classes=basic_classes(), plan_hours=10):
    try:
        return Plans.objects.get(employee=employee, classes=classes)
    except ObjectDoesNotExist:
        return Plans.objects.create(employee=employee, classes=classes, plan_hours=plan_hours)