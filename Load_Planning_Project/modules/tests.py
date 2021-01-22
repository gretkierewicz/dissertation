from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APIRequestFactory

from .models import Modules, Classes, Plans
from .serializers import ModuleSerializer, ClassSerializer, PlanSerializer

from employees.models import Pensum
from employees.tests import basic_supervisor
from utils.tests import StatusCodeTests

client = APIClient()
factory = APIRequestFactory()


def basic_module(name='basic_module'):
    try:
        return Modules.objects.get(module_code=name)
    except ObjectDoesNotExist:
        return Modules.objects.create(name=name, module_code=name)


def basic_classes(classes_hours=100, name='Lectures'):
    try:
        return Classes.objects.get(module=basic_module(), name=name)
    except ObjectDoesNotExist:
        return Classes.objects.create(module=basic_module(), name=name, classes_hours=classes_hours)


def basic_plans(employee, classes=basic_classes(), plan_hours=10):
    try:
        return Plans.objects.get(employee=employee, classes=classes)
    except ObjectDoesNotExist:
        return Plans.objects.create(employee=employee, classes=classes, plan_hours=plan_hours)


class ModuleTests(StatusCodeTests, TestCase):
    def setUp(self):
        self.basename = 'modules'
        self.model = Modules
        self.serializer = ModuleSerializer
        self.basic_element = basic_module()
        self.unique_element = basic_module(name='second_element')

        max_len = {'name': 45, 'module_code': 45}
        no_null_fields = ['name', 'module_code']
        valid_data = {'name': 'x', 'module_code': 'x'}

        self.valid_list_kwargs = {}
        self.valid_detail_kwargs = {'module_code': self.basic_element.module_code}
        self.invalid_detail_kwargs = {'module_code': 'some_random_slug'}

        self.valid_post_data = {'Valid data': valid_data}
        self.valid_put_data = self.valid_post_data
        self.valid_patch_data = {}
        for field, length in max_len.items():
            self.valid_patch_data['Max length ' + field] = {field: length * 'a'}
        self.valid_patch_data = {
            'Basic supervisor ': {'supervisor': factory.get(reverse(
                'employees-detail', kwargs={'abbreviation': basic_supervisor().abbreviation})).build_absolute_uri()},
            'No supervisor ': {'supervisor': None}}

        self.invalid_post_data = {
            'Not unique module_code': {'name': 'x', 'module_code': self.unique_element.module_code}
        }
        self.invalid_patch_data = {
            'Not unique module_code': {'module_code': self.unique_element.module_code}
        }
        for field in no_null_fields:
            self.invalid_post_data['Blank ' + field] = valid_data.copy()
            self.invalid_post_data['Blank ' + field][field] = ''
            self.invalid_patch_data['Blank ' + field] = {field: ''}
            self.invalid_patch_data['None ' + field] = {field: None}
        self.invalid_put_data = self.invalid_post_data

        for i in range(3):
            basic_module(name=f'module_{i}')


class ClassesTests(StatusCodeTests, TestCase):
    def setUp(self):
        self.basename = 'classes'
        self.model = Classes
        self.serializer = ClassSerializer
        self.basic_element = basic_classes()
        self.another_element = basic_classes(name=Classes.NAME_CHOICES[-1][0])

        no_null_fields = ['classes_hours']
        valid_data = {'module': factory.get(reverse('modules-detail', kwargs={'module_code': basic_module().module_code}
                                                    )).build_absolute_uri(),
                      'name': Classes.NAME_CHOICES[1][0],
                      'classes_hours': 10}

        self.valid_list_kwargs = {'module_module_code': basic_module().module_code}
        self.valid_detail_kwargs = {'name': self.basic_element.name, 'module_module_code': basic_module().module_code}
        self.invalid_detail_kwargs = {'name': 'x', 'module_module_code': basic_module('random').module_code}

        self.valid_post_data = {'Valid data': valid_data}
        self.valid_put_data = self.valid_post_data
        self.valid_patch_data = {
            'Min classes hours': {'classes_hours': 0},
            'High classes hours': {'classes_hours': 1000},
            # if name changed before hours, item cannot be reached by valid_detail_kwargs
            'Valid name': {'name': Classes.NAME_CHOICES[1][0]},
        }

        self.invalid_post_data = {
            'No module': {'module': None, 'name': valid_data['name'], 'classes_hours': 10},
            'No name': {'module': valid_data['module'], 'name': None, 'classes_hours': 10},
            'Not unique name': {'module': valid_data['module'], 'name': self.another_element.name, 'classes_hours': 10},
            'Negative hours': {'name': valid_data['name'], 'module': valid_data['module'], 'classes_hours': -1}
        }
        self.invalid_put_data = self.invalid_post_data
        self.invalid_put_data.pop('No module')
        self.invalid_patch_data = {
            'Not unique name': {'name': self.another_element.name},
            'Negative hours': {'classes_hours': -1}
        }


class PlansTests(StatusCodeTests, TestCase):
    def setUp(self):
        self.basename = 'plans'
        self.model = Plans
        self.serializer = PlanSerializer
        self.basic_element = basic_plans(employee=basic_supervisor(),
                                         classes=basic_classes(name=Classes.NAME_CHOICES[0][0]))
        self.another_element = basic_plans(employee=basic_supervisor('sup'),
                                           classes=basic_classes(name=Classes.NAME_CHOICES[-1][0]))
        self.basic_pensum = Pensum.objects.create(value=20, limit=80)
        self.basic_pensum.degrees.add(self.basic_element.employee.degree.pk)
        self.basic_pensum.positions.add(self.basic_element.employee.position.pk)

        valid_data = {
            'employee': factory.get(reverse('employees-detail', kwargs={
                'abbreviation': basic_supervisor('diff').abbreviation})).build_absolute_uri(),
            'classes': factory.get(reverse('classes-detail', kwargs={
                'module_module_code': self.basic_element.classes.module.module_code,
                'name': self.basic_element.classes.name})).build_absolute_uri(),
            'plan_hours': 11
        }

        self.valid_list_kwargs = {
            'module_module_code': self.basic_element.classes.module.module_code,
            'class_name': self.basic_element.classes.name
        }
        self.valid_detail_kwargs = self.valid_list_kwargs.copy()
        self.valid_detail_kwargs['employee'] = self.basic_element.employee.abbreviation
        self.invalid_detail_kwargs = {
            'module_module_code': self.basic_element.classes.module.module_code,
            'class_name': self.basic_element.classes.name,
            'employee': 'not_existing'
        }

        self.valid_post_data = {'Valid data': valid_data}
        self.valid_put_data = self.valid_post_data
        self.valid_patch_data = {
            'Min plan hours': {'plan_hours': 1},
            'Max plan hours': {'plan_hours': min(self.basic_element.classes.classes_hours, self.basic_pensum.limit)},
            'Valid employee': {'employee': valid_data['employee']},
        }

        self.invalid_post_data = {
            'No employee': {'employee': None, 'plan_hours': valid_data['plan_hours']},
            'Zero plan hours': {'employee': valid_data['employee'], 'plan_hours': 0},
            'Negative plan hours': {'employee': valid_data['employee'], 'plan_hours': -1},
            'Plan hours extending classes horus': {
                'employee': valid_data['employee'],
                'plan_hours': self.basic_element.classes.classes_hours + 1}
        }
        self.invalid_put_data = self.invalid_post_data
        self.invalid_patch_data = {
            'No employee': {'employee': None},
            'Zero plan hours': {'plan_hours': 0},
            'Negative plan hours': {'plan_hours': -1},
            'Plan hours extending classes horus': {'plan_hours': self.basic_element.classes.classes_hours + 1}
        }
