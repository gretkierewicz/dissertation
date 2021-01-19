from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APIRequestFactory

from .models import Modules
from .serializers import ModuleSerializer
from utils.tests import StatusCodeTests, basic_employee, basic_supervisor, basic_module

client = APIClient()
factory = APIRequestFactory()


class ModuleTests(StatusCodeTests, TestCase):
    def setUp(self):
        self.basename = 'modules'
        self.model = Modules
        self.serializer = ModuleSerializer
        self.basic_element = basic_module()

        max_len = {'name': 45, 'module_code': 45}
        no_null_fields = ['name', 'module_code']
        valid_data = {'name': 'x', 'module_code': 'x'}

        self.valid_lookup_kwargs = {'module_code': self.basic_element.module_code}
        self.valid_post_data = {'Valid data': valid_data}
        self.valid_put_data = self.valid_post_data

        self.valid_patch_data = {}
        for field, length in max_len.items():
            self.valid_patch_data['Max length ' + field] = {field: length * 'a'}
        self.valid_patch_data = {
            'Basic supervisor ': {'supervisor': factory.get(reverse(
                'employees-detail', kwargs={'abbreviation': basic_supervisor().abbreviation})).build_absolute_uri()},
            'No supervisor ': {'supervisor': None}}

        self.invalid_lookup_kwargs = {'module_code': 'some_random_slug'}
        self.invalid_post_data = {}
        self.invalid_patch_data = {}

        for field in no_null_fields:
            self.invalid_post_data['Blank ' + field] = valid_data.copy()
            self.invalid_post_data['Blank ' + field][field] = ''
            self.invalid_patch_data['Blank ' + field] = {field: ''}
            self.invalid_patch_data['None ' + field] = {field: None}

        self.invalid_put_data = self.invalid_post_data

        for i in range(3):
            basic_module(name=f'module_{i}')
