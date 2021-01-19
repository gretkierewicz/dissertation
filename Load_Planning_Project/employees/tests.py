from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory

from .models import Degrees, Positions, Employees, Pensum
from .serializers import DegreeSerializer, PositionSerializer, EmployeeSerializer, PensumSerializer
from utils.tests import StatusCodeTests, basic_degree, basic_position, basic_employee, basic_supervisor

client = APIClient()
factory = APIRequestFactory()


class DegreesTests(StatusCodeTests, TestCase):
    def setUp(self):
        self.basename = 'degrees'
        self.model = Degrees
        self.serializer = DegreeSerializer
        self.basic_element = basic_degree()

        self.name_max_len = 45

        self.valid_list_kwargs = {}
        self.valid_detail_kwargs = {'pk': self.basic_element.pk}
        self.invalid_detail_kwargs = {'pk': 1000}

        self.valid_post_data = {'Valid name': {'name': self.name_max_len * 'x'}}
        self.valid_put_data = self.valid_post_data
        self.valid_patch_data = self.valid_put_data

        self.invalid_post_data = {'Blank name': {'name': ''}, 'Too long name': {'name': self.name_max_len*'x'+'x'}}
        self.invalid_put_data = self.invalid_post_data
        self.invalid_patch_data = self.invalid_put_data

        for i in range(3):
            Degrees.objects.create(name=f'degree {i}')

    def test_delete_valid_data(self):
        self.method_simple_test(function=client.delete, url_suffix='detail', url_kwargs=self.valid_detail_kwargs,
                                status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_invalid_data(self):
        self.method_simple_test(function=client.delete, url_suffix='detail', url_kwargs=self.invalid_detail_kwargs,
                                status_code=status.HTTP_405_METHOD_NOT_ALLOWED)


class PositionsTests(DegreesTests, TestCase):
    def setUp(self):
        self.basename = 'positions'
        self.model = Positions
        self.serializer = PositionSerializer
        self.basic_element = basic_position()

        self.name_max_len = 45

        self.valid_list_kwargs = {}
        self.valid_detail_kwargs = {'pk': self.basic_element.pk}
        self.invalid_detail_kwargs = {'pk': 1000}

        self.valid_post_data = {'Valid name': {'name': self.name_max_len * 'x'}}
        self.valid_put_data = self.valid_post_data
        self.valid_patch_data = self.valid_put_data

        self.invalid_post_data = {'Blank name': {'name': ''}, 'Too long name': {'name': self.name_max_len*'x'+'x'}}
        self.invalid_put_data = self.invalid_post_data
        self.invalid_patch_data = self.invalid_put_data

        for i in range(3):
            Positions.objects.create(name=f'position {i}')


class EmployeesTests(StatusCodeTests, TestCase):
    def setUp(self):
        self.basename = 'employees'
        self.model = Employees
        self.serializer = EmployeeSerializer
        self.basic_element = basic_employee()

        max_len = {'first_name': 45, 'last_name': 45, 'abbreviation': 5, 'e_mail': 45}
        no_null_fields = ['first_name', 'last_name', 'abbreviation', 'e_mail']
        valid_data = {'first_name': 'x',
                      'last_name': 'x',
                      'abbreviation': 'x',
                      'degree': basic_degree().pk,
                      'position': basic_position().pk,
                      'e_mail': 'x@x.xx'}

        self.valid_list_kwargs = {}
        self.valid_detail_kwargs = {'abbreviation': self.basic_element.abbreviation}
        self.invalid_detail_kwargs = {'abbreviation': 'some_random_slag'}

        self.valid_post_data = {'Valid data': valid_data}
        self.valid_put_data = self.valid_post_data
        self.valid_patch_data = {}
        for field, length in max_len.items():
            self.valid_patch_data['Max length ' + field] = {field: length * 'a'}
        self.valid_patch_data = {'Basic supervisor ': {'supervisor': basic_supervisor().pk},
                                 'No supervisor ': {'supervisor': None},
                                 'Min year_of_studies': {'year_of_studies': 0},
                                 'High year_of_studies': {'year_of_studies': 100}}

        self.invalid_post_data = {'No degree': valid_data.copy()}
        self.invalid_post_data['No degree']['degree'] = None
        self.invalid_post_data = {'No position': valid_data.copy()}
        self.invalid_post_data['No position']['position'] = None
        self.invalid_patch_data = {'No degree': {'degree': None},
                                   'No position': {'position': None}}
        for field in no_null_fields:
            self.invalid_post_data['Blank ' + field] = valid_data.copy()
            self.invalid_post_data['Blank ' + field][field] = ''
            self.invalid_patch_data['Blank ' + field] = {field: ''}
            self.invalid_patch_data['None ' + field] = {field: None}
        self.invalid_put_data = self.invalid_post_data

        for i in range(3):
            Employees.objects.create(
                first_name=f'first_name {i}',
                last_name=f'last_name {i}',
                abbreviation=f'abb{i}',
                degree=basic_degree(),
                position=basic_position(),
                e_mail=f'e.mail.{i}@x.xx')


class PensumTests(StatusCodeTests, TestCase):
    def setUp(self):
        self.basename = 'pensum'
        self.model = Pensum
        self.serializer = PensumSerializer
        self.basic_element = Pensum.objects.create(value=15, limit=95)
        self.basic_element.degrees.add(basic_degree().pk)
        self.basic_element.positions.add(basic_position().pk)
        self.another_element = Pensum.objects.create(value=30, limit=40)
        self.another_element.degrees.add(basic_degree('another_degree').pk)
        self.another_element.positions.add(basic_position('another_position').pk)

        self.valid_list_kwargs = {}
        self.valid_detail_kwargs = {'pk': self.basic_element.pk}
        self.invalid_detail_kwargs = {'pk': 1000}

        self.valid_post_data = {'Valid data': {'value': 10, 'limit': 20,
                                               'degrees': [basic_degree('valid degree').pk],
                                               'positions': [basic_position('valid position').pk]}}
        self.valid_put_data = self.valid_post_data
        self.valid_patch_data = {'Valid value': {'value': 15},
                                 'Valid limit': {'limit': 95},
                                 'Valid degrees': {'degrees': [basic_degree('valid degree').pk]},
                                 'Valid positions': {'positions': [basic_position('valid position').pk]}}

        self.invalid_post_data = {
            'Existing degree and position match': {'value': 50, 'limit': 60,
                                                   'degrees': [basic_degree('another_degree').pk],
                                                   'positions': [basic_position('another_position').pk]},
            'Value greater than limit': {'value': 90, 'limit': 10,
                                         'degrees': [basic_degree('valid degree A').pk],
                                         'positions': [basic_position('valid position A').pk]},
            'Value equal to limit': {'value': 100, 'limit': 100,
                                     'degrees': [basic_degree('valid degree B').pk],
                                     'positions': [basic_position('valid position B').pk]}
        }
        self.invalid_put_data = {
            'Existing degree and position match': {'value': 70, 'limit': 80,
                                                   'degrees': [basic_degree('another_degree').pk],
                                                   'positions': [basic_position('another_position').pk]},
            'Value greater than limit': {'value': 90, 'limit': 10,
                                         'degrees': [basic_degree('valid degree A').pk],
                                         'positions': [basic_position('valid position A').pk]},
            'Value equal to limit': {'value': 100, 'limit': 100,
                                     'degrees': [basic_degree('valid degree B').pk],
                                     'positions': [basic_position('valid position B').pk]}
        }
        self.invalid_patch_data = {'Value greater than limit': {'value': 1000},
                                   'Value equal to limit': {'value': self.basic_element.limit},
                                   'Limit lower than value': {'limit': 1},
                                   'Limit equal to value': {'limit': self.basic_element.value}}
