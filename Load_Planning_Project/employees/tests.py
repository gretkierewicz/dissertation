from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory

from .models import Degrees, Positions, Employees
from .serializers import DegreeSerializer, PositionSerializer, EmployeeSerializer
from utils.tests import BasicMethodsTests, basic_degree, basic_position, basic_employee, basic_supervisor

client = APIClient()
factory = APIRequestFactory()


class DegreesTests(BasicMethodsTests, TestCase):
    def setUp(self):
        self.basename = 'degrees'
        self.model = Degrees
        self.serializer = DegreeSerializer
        self.basic_element = basic_degree()

        self.name_max_len = 45

        self.valid_lookup_kwargs = {'pk': self.basic_element.pk}
        self.valid_post_data = {'Valid name': {'name': self.name_max_len * 'x'}}
        self.valid_put_data = self.valid_post_data
        self.valid_patch_data = self.valid_put_data

        self.invalid_lookup_kwargs = {'pk': 1000}
        self.invalid_post_data = {'Blank name': {'name': ''}, 'Too long name': {'name': self.name_max_len*'x'+'x'}}
        self.invalid_put_data = self.invalid_post_data
        self.invalid_patch_data = self.invalid_put_data

        for i in range(3):
            Degrees.objects.create(name=f'degree {i}')

    def test_delete_valid_data(self):
        self.method_simple_test(function=client.delete, url_suffix='detail', url_kwargs=self.valid_lookup_kwargs,
                                status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_invalid_data(self):
        self.method_simple_test(function=client.delete, url_suffix='detail', url_kwargs=self.invalid_lookup_kwargs,
                                status_code=status.HTTP_405_METHOD_NOT_ALLOWED)


class PositionsTests(DegreesTests, TestCase):
    def setUp(self):
        self.basename = 'positions'
        self.model = Positions
        self.serializer = PositionSerializer
        self.basic_element = basic_position()

        self.name_max_len = 45

        self.valid_lookup_kwargs = {'pk': self.basic_element.pk}
        self.valid_post_data = {'Valid name': {'name': self.name_max_len * 'x'}}
        self.valid_put_data = self.valid_post_data
        self.valid_patch_data = self.valid_put_data

        self.invalid_lookup_kwargs = {'pk': 1000}
        self.invalid_post_data = {'Blank name': {'name': ''}, 'Too long name': {'name': self.name_max_len*'x'+'x'}}
        self.invalid_put_data = self.invalid_post_data
        self.invalid_patch_data = self.invalid_put_data

        for i in range(3):
            Positions.objects.create(name=f'position {i}')


class EmployeesTests(BasicMethodsTests, TestCase):
    def setUp(self):
        self.basename = 'employees'
        self.model = Employees
        self.serializer = EmployeeSerializer
        self.basic_element = basic_employee()

        max_len = {'first_name': 45, 'last_name': 45, 'abbreviation': 5, 'e_mail': 45}
        valid_data = {'first_name': 'x',
                      'last_name': 'x',
                      'abbreviation': 'x',
                      'degree': basic_degree().pk,
                      'position': basic_position().pk,
                      'e_mail': 'x@x.xx'}

        self.valid_lookup_kwargs = {'abbreviation': self.basic_element.abbreviation}
        self.valid_post_data = {'Valid data': valid_data}
        self.valid_put_data = self.valid_post_data

        self.valid_patch_data = {}
        for field in ['first_name', 'last_name', 'abbreviation', 'e_mail']:
            self.valid_patch_data['Max length ' + field] = {field: max_len[field] * 'asdax'}
        self.valid_patch_data = {'Basic supervisor ': {'supervisor': basic_supervisor().pk},
                                 'No supervisor ': {'supervisor': None},
                                 'Min year_of_studies': {'year_of_studies': 0},
                                 'High year_of_studies': {'year_of_studies': 100}}

        self.invalid_lookup_kwargs = {'abbreviation': 'some_random_slag'}

        self.invalid_post_data = {'No degree': valid_data.copy()}
        self.invalid_post_data['No degree']['degree'] = None
        self.invalid_post_data = {'No position': valid_data.copy()}
        self.invalid_post_data['No position']['position'] = None
        self.invalid_patch_data = {'No degree': {'degree': None},
                                   'No position': {'position': None}}

        for field in ['first_name', 'last_name', 'abbreviation', 'e_mail']:
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
