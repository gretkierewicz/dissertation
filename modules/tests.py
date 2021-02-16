import json

from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APIRequestFactory, APITestCase

from .models import Modules, Classes
from .serializers import ModuleSerializer, ClassSerializer

from employees.models import Degrees, Positions, Employees
from employees.tests import EmployeeFields

from utils.random_generators import random_max_len_field_str, random_bool, random_str
from utils.tests import BasicAPITests


client = APIClient()
factory = APIRequestFactory()


class ModuleFields:
    module_code = 'module_code'
    name = 'name'
    examination = 'examination'
    supervisor = 'supervisor'


class ModuleTests(BasicAPITests, APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.factory = APIRequestFactory()

        cls.model = Modules
        cls.serializer = ModuleSerializer
        cls.list_serializer = cls.serializer
        cls.list_view_name = 'modules-list'
        cls.detail_view_name = 'modules-detail'
        cls.context = {'request': cls.factory.get(reverse(cls.list_view_name), format=json)}
        cls.lookup = ModuleFields.module_code
        cls.field_lookup = cls.lookup
        cls.delete_forbidden = False

        def create_employee():
            return Employees.objects.create(**{
                EmployeeFields.first_name: random_max_len_field_str(Employees, EmployeeFields.first_name),
                EmployeeFields.last_name: random_max_len_field_str(Employees, EmployeeFields.last_name),
                EmployeeFields.abbreviation: random_max_len_field_str(Employees, EmployeeFields.abbreviation),
                EmployeeFields.e_mail: random_max_len_field_str(Employees, EmployeeFields.e_mail)[:-6] + '@ab.ba',
                EmployeeFields.degree: Degrees.objects.create(name=random_str(5)),
                EmployeeFields.position: Positions.objects.create(name=random_str(5))
            })

        def create_model_data():
            return {
                ModuleFields.module_code: random_max_len_field_str(cls.model, ModuleFields.module_code),
                ModuleFields.name: random_max_len_field_str(cls.model, ModuleFields.name),
                ModuleFields.supervisor: create_employee(),
            }

        cls.obj = cls.model.objects.create(**create_model_data())
        for i in range(3):
            cls.model.objects.create(**create_model_data())

        def create_payload_data():
            return {
                ModuleFields.module_code: random_max_len_field_str(cls.model, ModuleFields.module_code),
                ModuleFields.name: random_max_len_field_str(cls.model, ModuleFields.name),
                ModuleFields.supervisor: create_employee().abbreviation,
            }

        cls.valid_post_data_payload = {
            'max length': {**create_payload_data()},
            'short': {
                ModuleFields.module_code: random_str(1),
                ModuleFields.name: random_str(1),
                ModuleFields.supervisor: create_employee().abbreviation,
            },
            'complete': {
                **create_payload_data(),
                ModuleFields.examination: random_bool(),
            }
        }

        cls.valid_put_data_payload = cls.valid_post_data_payload

        cls.valid_partial_data = {
            'max length ' + ModuleFields.module_code: {
                ModuleFields.module_code: random_max_len_field_str(cls.model, ModuleFields.module_code)},
            'short ' + ModuleFields.module_code: {ModuleFields.module_code: random_str(1)},
            'max length ' + ModuleFields.name: {
                ModuleFields.name: random_max_len_field_str(cls.model, ModuleFields.name)},
            'short ' + ModuleFields.name: {ModuleFields.name: random_str(1)},
            'True ' + ModuleFields.examination: {ModuleFields.examination: True},
            'False ' + ModuleFields.examination: {ModuleFields.examination: False},
            'new ' + ModuleFields.supervisor: {ModuleFields.supervisor: create_employee().abbreviation},
            'not unique ' + ModuleFields.supervisor: {
                ModuleFields.supervisor: cls.model.objects.exclude(pk=cls.obj.pk).first().supervisor.abbreviation
            },
        }

        cls.invalid_post_data_payload = {
            'too long ' + ModuleFields.module_code: {
                **create_payload_data(),
                ModuleFields.module_code: random_max_len_field_str(cls.model, ModuleFields.module_code) + random_str(1),
            },
            'empty ' + ModuleFields.module_code: {
                **create_payload_data(),
                ModuleFields.module_code: '',
            },
            'too long ' + ModuleFields.name: {
                **create_payload_data(),
                ModuleFields.name: random_max_len_field_str(cls.model, cls.field_lookup) + random_str(1),
            },
            'empty ' + ModuleFields.name: {
                **create_payload_data(),
                ModuleFields.name: '',
            },
        }

        cls.invalid_put_data_payload = cls.invalid_post_data_payload

        cls.invalid_partial_data = {
            'too long ' + ModuleFields.module_code: {
                ModuleFields.module_code: random_max_len_field_str(cls.model, ModuleFields.module_code) + random_str(1),
            },
            'empty ' + ModuleFields.module_code: {ModuleFields.module_code: ''},
            'not unique ' + ModuleFields.module_code: {
                ModuleFields.module_code: cls.model.objects.exclude(pk=cls.obj.pk).first().module_code},
            'too long ' + ModuleFields.name: {
                ModuleFields.name: random_max_len_field_str(cls.model, cls.field_lookup) + random_str(1)
            },
            'empty ' + ModuleFields.name: {ModuleFields.name: ''},
            # TODO: Check if empty supervisor is valid or invalid data for module
            #'empty ' + ModuleFields.supervisor: {ModuleFields.supervisor: None},
        }
