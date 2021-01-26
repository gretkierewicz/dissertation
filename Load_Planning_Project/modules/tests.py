import json
import random

from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APIRequestFactory

from employees.models import Degrees, Positions, Employees
from employees.tests import DegreesTests, EmpFields

from .models import Modules, Classes, Plans
from .serializers import ModuleSerializer, ClassSerializer, PlanSerializer


client = APIClient()
factory = APIRequestFactory()


class ModuleTests(DegreesTests):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.factory = APIRequestFactory()

        module_code = 'module_code'
        name = 'name'
        examination = 'examination'
        supervisor = 'supervisor'

        cls.model = Modules
        cls.serializer = ModuleSerializer
        cls.list_serializer = cls.serializer
        cls.basename = 'modules'
        cls.context = {'request': cls.factory.get(reverse(cls.basename + '-list'), format=json)}
        cls.lookup = 'module_code'
        cls.field_lookup = cls.lookup
        cls.delete_forbidden = False

        def create_employee():
            return Employees.objects.create(**{
                EmpFields.first_name: cls.get_random_field_str(Employees, EmpFields.first_name),
                EmpFields.last_name: cls.get_random_field_str(Employees, EmpFields.last_name),
                EmpFields.abbreviation: cls.get_random_field_str(Employees, EmpFields.abbreviation),
                EmpFields.e_mail: cls.get_random_field_str(Employees, EmpFields.e_mail)[:-6] + '@ab.ba',
                EmpFields.degree: Degrees.objects.create(name=cls.get_random_str(5)),
                EmpFields.position: Positions.objects.create(name=cls.get_random_str(5))
            })

        def create_model_data():
            return {
                module_code: cls.get_random_field_str(cls.model, module_code),
                name: cls.get_random_field_str(cls.model, name),
                supervisor: create_employee(),
            }

        cls.obj = cls.model.objects.create(**create_model_data())
        for i in range(3):
            cls.model.objects.create(**create_model_data())

        def create_payload_data():
            return {
                module_code: cls.get_random_field_str(cls.model, module_code),
                name: cls.get_random_field_str(cls.model, name),
                supervisor: create_employee().abbreviation,
            }

        cls.valid_post_data_payload = {
            'max length': {**create_payload_data()},
            'short': {
                module_code: cls.get_random_str(1),
                name: cls.get_random_str(1),
                supervisor: create_employee().abbreviation,
            },
            'complete': {
                **create_payload_data(),
                examination: random.choices([True, False])[0],
            }
        }

        cls.valid_put_data_payload = cls.valid_post_data_payload

        cls.valid_partial_data = {
            'max length ' + module_code: {module_code: cls.get_random_field_str(cls.model, module_code)},
            'short ' + module_code: {module_code: cls.get_random_str(1)},
            'max length ' + name: {name: cls.get_random_field_str(cls.model, name)},
            'short ' + name: {name: cls.get_random_str(1)},
            'True ' + examination: {examination: True},
            'False ' + examination: {examination: False},
            'new ' + supervisor: {supervisor: create_employee().abbreviation},
            'not unique ' + supervisor: {
                supervisor: cls.model.objects.exclude(pk=cls.obj.pk).first().supervisor.abbreviation
            },
        }

        cls.invalid_post_data_payload = {
            'too long ' + module_code: {
                **create_payload_data(),
                module_code: cls.get_random_field_str(cls.model, module_code) + cls.get_random_str(1),
            },
            'empty ' + module_code: {
                **create_payload_data(),
                module_code: '',
            },
            'too long ' + name: {
                **create_payload_data(),
                name: cls.get_random_field_str(cls.model, cls.field_lookup) + cls.get_random_str(1),
            },
            'empty ' + name: {
                **create_payload_data(),
                name: '',
            },
        }

        cls.invalid_put_data_payload = cls.invalid_post_data_payload

        cls.invalid_partial_data = {
            'too long ' + module_code: {
                module_code: cls.get_random_field_str(cls.model, module_code) + cls.get_random_str(1),
            },
            'empty ' + module_code: {module_code: ''},
            'not unique ' + module_code: {module_code: cls.model.objects.exclude(pk=cls.obj.pk).first().module_code},
            'too long ' + name: {
                name: cls.get_random_field_str(cls.model, cls.field_lookup) + cls.get_random_str(1)
            },
            'empty ' + name: {name: ''},
            # TODO: Check if empty supervisor is valid or invalid data for module
            #'empty ' + supervisor: {supervisor: None},
        }
