import json

from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APIRequestFactory, APITestCase

from utils.random_generators import random_max_len_field_str, random_str
from utils.tests import BasicAPITests
from .models import Degrees, Employees, Positions
from .serializers import DegreeSerializer, EmployeeListSerializer, EmployeeSerializer, PositionSerializer


class DegreeFields:
    name = 'name'


class PositionFields:
    name = 'name'


class EmployeeFields:
    first_name = 'first_name'
    last_name = 'last_name'
    abbreviation = 'abbreviation'
    e_mail = 'e_mail'
    degree = 'degree'
    position = 'position'

    string_fields = (first_name, last_name, abbreviation, e_mail)


class DegreesTests(BasicAPITests, APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.factory = APIRequestFactory()

        cls.model = Degrees
        cls.serializer = DegreeSerializer
        cls.list_serializer = cls.serializer
        cls.list_view_name = 'degrees-list'
        cls.detail_view_name = 'degrees-detail'
        cls.context = {'request': cls.factory.get(reverse(cls.list_view_name), format=json)}
        cls.lookup = 'pk'
        cls.field_lookup = DegreeFields.name
        cls.delete_forbidden = True

        cls.obj_data = {cls.field_lookup: random_max_len_field_str(cls.model, cls.field_lookup)}
        cls.obj = cls.model.objects.create(**cls.obj_data)
        for i in range(3):
            cls.model.objects.create(name=random_max_len_field_str(cls.model, cls.field_lookup))

        cls.valid_post_data_payload = {
            'max length': {DegreeFields.name: random_max_len_field_str(cls.model, cls.field_lookup)},
            'short': {DegreeFields.name: random_str(1)},
        }

        cls.valid_put_data_payload = cls.valid_post_data_payload
        cls.valid_partial_data = cls.valid_post_data_payload

        cls.invalid_post_data_payload = {
            'over max length': {DegreeFields.name: random_max_len_field_str(cls.model, cls.field_lookup) + 'x'},
            'empty string': {DegreeFields.name: ''},
        }

        cls.invalid_put_data_payload = cls.invalid_post_data_payload
        cls.invalid_partial_data = cls.invalid_post_data_payload


class PositionsTests(BasicAPITests, APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.factory = APIRequestFactory()

        cls.model = Positions
        cls.serializer = PositionSerializer
        cls.list_serializer = cls.serializer
        cls.list_view_name = 'positions-list'
        cls.detail_view_name = 'positions-detail'
        cls.context = {'request': cls.factory.get(reverse(cls.list_view_name), format=json)}
        cls.lookup = 'pk'
        cls.field_lookup = PositionFields.name
        cls.delete_forbidden = True

        cls.obj_data = {cls.field_lookup: random_max_len_field_str(cls.model, cls.field_lookup)}
        cls.obj = cls.model.objects.create(**cls.obj_data)
        for i in range(3):
            cls.model.objects.create(name=random_max_len_field_str(cls.model, cls.field_lookup))

        cls.valid_post_data_payload = {
            'max length': {PositionFields.name: random_max_len_field_str(cls.model, cls.field_lookup)},
            'short': {PositionFields.name: random_str(1)},
        }

        cls.valid_put_data_payload = cls.valid_post_data_payload
        cls.valid_partial_data = cls.valid_post_data_payload

        cls.invalid_post_data_payload = {
            'over max length': {PositionFields.name: random_max_len_field_str(cls.model, cls.field_lookup) + 'x'},
            'empty string': {PositionFields.name: ''},
        }

        cls.invalid_put_data_payload = cls.invalid_post_data_payload
        cls.invalid_partial_data = cls.invalid_post_data_payload


class EmployeesTests(BasicAPITests, APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.factory = APIRequestFactory()

        cls.model = Employees
        cls.serializer = EmployeeSerializer
        cls.list_serializer = EmployeeListSerializer
        cls.list_view_name = 'employees-list'
        cls.detail_view_name = 'employees-detail'
        cls.context = {'request': cls.factory.get(reverse(cls.list_view_name), format=json)}
        cls.lookup = EmployeeFields.abbreviation
        cls.field_lookup = cls.lookup
        cls.delete_forbidden = False

        def create_model_data():
            return {
                EmployeeFields.first_name: random_max_len_field_str(cls.model, EmployeeFields.first_name),
                EmployeeFields.last_name: random_max_len_field_str(cls.model, EmployeeFields.last_name),
                EmployeeFields.abbreviation: random_max_len_field_str(cls.model, EmployeeFields.abbreviation),
                EmployeeFields.e_mail: random_max_len_field_str(cls.model, EmployeeFields.e_mail)[:-6] + '@ab.ba',
                EmployeeFields.degree: Degrees.objects.create(name=random_str(5)),
                EmployeeFields.position: Positions.objects.create(name=random_str(5))
            }

        cls.obj = cls.model.objects.create(**create_model_data())
        for i in range(3):
            cls.model.objects.create(**create_model_data())

        def create_payload_data():
            return {
                EmployeeFields.first_name: random_max_len_field_str(cls.model, EmployeeFields.first_name),
                EmployeeFields.last_name: random_max_len_field_str(cls.model, EmployeeFields.last_name),
                EmployeeFields.abbreviation: random_max_len_field_str(cls.model, EmployeeFields.abbreviation),
                EmployeeFields.e_mail: random_max_len_field_str(cls.model, EmployeeFields.e_mail)[:-6] + '@ab.ba',
                EmployeeFields.degree: Degrees.objects.create(name=random_str(5)).name,
                EmployeeFields.position: Positions.objects.create(name=random_str(5)).name,
            }

        cls.valid_post_data_payload = {
            'max length': create_payload_data(),
            'short strings': {
                EmployeeFields.first_name: random_str(1),
                EmployeeFields.last_name: random_str(1),
                EmployeeFields.abbreviation: random_str(1),
                EmployeeFields.e_mail: random_str(1) + '@ab.ba',
                EmployeeFields.degree: Degrees.objects.create(name=random_str(5)).name,
                EmployeeFields.position: Positions.objects.create(name=random_str(5)).name,
            },
            'all fields': {
                **create_payload_data(),
            }
        }

        cls.valid_put_data_payload = cls.valid_post_data_payload

        cls.valid_partial_data = {
            'max length ' + EmployeeFields.first_name: {
                EmployeeFields.first_name: random_max_len_field_str(cls.model, EmployeeFields.first_name)
            }
        }

        rand_abbreviation = random_max_len_field_str(cls.model, EmployeeFields.abbreviation)
        cls.invalid_post_data_payload = {
            'empty ' + EmployeeFields.first_name: {**create_payload_data(), EmployeeFields.first_name: ''},
        }

        cls.invalid_put_data_payload = {
            **cls.invalid_post_data_payload,
        }
        cls.invalid_partial_data = {}
        for field in EmployeeFields.string_fields:
            cls.invalid_partial_data['empty ' + field] = {**create_payload_data(), field: ''}
            cls.invalid_partial_data['too long ' + field] = {
                **create_payload_data(),
                field: random_max_len_field_str(cls.model, EmployeeFields.first_name) + random_str(1)}

        cls.invalid_partial_data = {}
        for field in EmployeeFields.string_fields:
            cls.invalid_partial_data['empty ' + field] = {field: ''}
            cls.invalid_partial_data['too long ' + field] = {
                field: random_max_len_field_str(cls.model, EmployeeFields.first_name) + random_str(1)}