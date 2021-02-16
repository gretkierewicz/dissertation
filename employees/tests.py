import json
import random

from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APIRequestFactory, APITestCase

from .models import Degrees, Positions, Employees, Pensum
from .serializers import DegreeSerializer, PositionSerializer, EmployeeSerializer, PensumSerializer, \
    EmployeeListSerializer

from utils.constants import NA
from utils.random_generators import random_max_len_field_str, random_str, random_bool
from utils.tests import BasicAPITests


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
    supervisor = 'supervisor'
    year_of_studies = 'year_of_studies'
    is_procedure_for_a_doctoral_degree_approved = 'is_procedure_for_a_doctoral_degree_approved'
    has_scholarship = 'has_scholarship'

    string_fields = (first_name, last_name, abbreviation, e_mail)


class PensumFields:
    name = 'name'
    value = 'value'
    limit = 'limit'
    degrees = 'degrees'
    positions = 'positions'
    year_of_studies = 'year_of_studies'
    year_condition = 'year_condition'
    is_procedure_for_a_doctoral_degree_approved = 'is_procedure_for_a_doctoral_degree_approved'
    has_scholarship = 'has_scholarship'


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
                'supervisor': None,
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
                EmployeeFields.supervisor: None,
            },
            'all fields': {
                **create_payload_data(),
                EmployeeFields.supervisor: Employees.objects.create(**create_model_data()).abbreviation,
                EmployeeFields.year_of_studies: random.randint(1, 100),
                EmployeeFields.is_procedure_for_a_doctoral_degree_approved: random_bool(),
                EmployeeFields.has_scholarship: random_bool(),
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
            'self supervising with new abbreviation': {
                **create_payload_data(), 'abbreviation': rand_abbreviation, 'supervisor': rand_abbreviation}
        }

        cls.invalid_put_data_payload = {
            **cls.invalid_post_data_payload,
            'self supervising with old abbreviation': {
                **create_payload_data(), 'abbreviation': cls.obj.abbreviation, 'supervisor': cls.obj.abbreviation
            }
        }
        cls.invalid_partial_data = {}
        for field in EmployeeFields.string_fields:
            cls.invalid_partial_data['empty ' + field] = {**create_payload_data(), field: ''}
            cls.invalid_partial_data['too long ' + field] = {
                **create_payload_data(),
                field: random_max_len_field_str(cls.model, EmployeeFields.first_name) + random_str(1)}

        cls.invalid_partial_data = {
            'self supervising': {'supervisor': cls.obj.abbreviation}}
        for field in EmployeeFields.string_fields:
            cls.invalid_partial_data['empty ' + field] = {field: ''}
            cls.invalid_partial_data['too long ' + field] = {
                field: random_max_len_field_str(cls.model, EmployeeFields.first_name) + random_str(1)}


class PensumTests(BasicAPITests, APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.factory = APIRequestFactory()

        cls.model = Pensum
        cls.serializer = PensumSerializer
        cls.list_serializer = cls.serializer
        cls.list_view_name = 'pensum-list'
        cls.detail_view_name = 'pensum-detail'
        cls.context = {'request': cls.factory.get(reverse(cls.list_view_name), format=json)}
        cls.lookup = 'pk'
        cls.field_lookup = PensumFields.name
        cls.delete_forbidden = False

        def create_model_data():
            return {
                PensumFields.name: random_max_len_field_str(cls.model, PensumFields.name),
                PensumFields.value: random.randint(1, 500),
                PensumFields.limit: random.randint(501, 1000),
            }

        cls.obj = cls.model.objects.create(**create_model_data())
        cls.obj.degrees.create(name=random_str(15))
        cls.obj.positions.create(name=random_str(15))
        cls.obj.degrees.create(name=random_str(15))
        cls.obj.positions.create(name=random_str(15))
        for i in range(3):
            pensum = cls.model.objects.create(**create_model_data())
            pensum.degrees.create(name=random_str(15))
            pensum.positions.create(name=random_str(15))
            pensum.degrees.create(name=random_str(15))
            pensum.positions.create(name=random_str(15))

        active_year_choices = [a for a, b in Pensum.YEAR_CONDITION_CHOICES if a != NA]
        active_procedure_choices = [a for a, b in Pensum.DOCTORAL_PROCEDURE_CHOICES if a != NA]
        active_scholarship_choices = [a for a, b in Pensum.SCHOLARSHIP_CHOICES if a != NA]

        duplicate = cls.model.objects.create(**{
            **create_model_data(),
            PensumFields.year_of_studies: random.randint(1, 20),
            PensumFields.year_condition: random.choice(active_year_choices),
            PensumFields.is_procedure_for_a_doctoral_degree_approved: random.choice(active_procedure_choices),
            PensumFields.has_scholarship: random.choice(active_scholarship_choices),
        })
        duplicate.degrees.create(name=random_str(15))
        duplicate.positions.create(name=random_str(15))

        def create_payload_data():
            return {
                PensumFields.name: random_max_len_field_str(cls.model, PensumFields.name),
                PensumFields.value: random.randint(1, 500),
                PensumFields.limit: random.randint(501, 1000),
                PensumFields.degrees: [
                    Degrees.objects.create(name=random_str(15)).name,
                    Degrees.objects.create(name=random_str(15)).name
                ],
                PensumFields.positions: [
                    Positions.objects.create(name=random_str(15)).name,
                    Positions.objects.create(name=random_str(15)).name
                ],
            }

        cls.valid_post_data_payload = {
            'max length': {**create_payload_data()},
            'short': {**create_payload_data(), 'name': random_str(1)},
            f'same {PensumFields.degrees}  & {PensumFields.positions} but different {PensumFields.year_condition} & '
            f'{PensumFields.year_of_studies}': {
                **create_payload_data(),
                PensumFields.degrees: [_.name for _ in cls.obj.degrees.all()],
                PensumFields.positions: [_.name for _ in cls.obj.positions.all()],
                PensumFields.year_of_studies: random.randint(1, 20),
                PensumFields.year_condition: random.choice(active_year_choices),
                PensumFields.is_procedure_for_a_doctoral_degree_approved: NA,
                PensumFields.has_scholarship: NA,
            },
            'completed data': {
                **create_payload_data(),
                PensumFields.year_of_studies: random.randint(1, 20),
                PensumFields.year_condition: random.choice(active_year_choices),
                PensumFields.is_procedure_for_a_doctoral_degree_approved: random.choice(active_procedure_choices),
                PensumFields.has_scholarship: random.choice(active_scholarship_choices),
            }
        }

        cls.valid_put_data_payload = cls.valid_post_data_payload

        cls.valid_partial_data = {
            f'max length {PensumFields.name}': {
                PensumFields.name: random_max_len_field_str(cls.model, PensumFields.name)},
            'min ' + PensumFields.value: {PensumFields.value: 0},
            'min ' + PensumFields.limit: {PensumFields.limit: 1},
            'high ' + PensumFields.limit: {PensumFields.limit: 2000},
            'high ' + PensumFields.value: {PensumFields.value: 1999},
            'no ' + PensumFields.limit: {PensumFields.limit: None},
            'rand ' + PensumFields.value: {PensumFields.value: 333},
            'min ' + PensumFields.limit: {PensumFields.limit: 334},
        }

        cls.invalid_post_data_payload = {
            'too long ' + PensumFields.name: {
                **create_payload_data(),
                PensumFields.name: random_max_len_field_str(cls.model, PensumFields.name) + random_str(1)},
            'empty ' + PensumFields.name: {**create_payload_data(), PensumFields.name: ''},
            'duplicate ' + PensumFields.degrees + '-' + PensumFields.positions: {
                **create_payload_data(),
                PensumFields.degrees: [cls.obj.degrees.first().name],
                PensumFields.positions: [cls.obj.positions.first().name],
                PensumFields.year_condition: NA,
                PensumFields.is_procedure_for_a_doctoral_degree_approved: NA,
                PensumFields.has_scholarship: NA,
            },
            'duplicate ' + PensumFields.year_of_studies + ' and ' + PensumFields.year_condition: {
                **create_payload_data(),
                PensumFields.degrees: [cls.obj.degrees.first().name],
                PensumFields.positions: [cls.obj.positions.first().name],
                PensumFields.year_of_studies: cls.obj.year_of_studies,
                PensumFields.year_condition: cls.obj.year_condition,
                PensumFields.is_procedure_for_a_doctoral_degree_approved: NA,
                PensumFields.has_scholarship: NA,
            }
        }

        cls.invalid_put_data_payload = {
            'duplicate ' + PensumFields.degrees + '-' + PensumFields.positions: {
                **create_payload_data(),
                PensumFields.degrees: [duplicate.degrees.first().name],
                PensumFields.positions: [duplicate.positions.first().name],
                PensumFields.year_condition: NA,
                PensumFields.is_procedure_for_a_doctoral_degree_approved: NA,
                PensumFields.has_scholarship: NA,
            },
            'duplicate ' + PensumFields.year_of_studies + ' and ' + PensumFields.year_condition: {
                **create_payload_data(),
                PensumFields.degrees: [duplicate.degrees.first().name],
                PensumFields.positions: [duplicate.positions.first().name],
                PensumFields.year_of_studies: duplicate.year_of_studies,
                PensumFields.year_condition: duplicate.year_condition,
                PensumFields.is_procedure_for_a_doctoral_degree_approved: NA,
                PensumFields.has_scholarship: NA,
            },
            'duplicate ' + PensumFields.is_procedure_for_a_doctoral_degree_approved: {
                **create_payload_data(),
                PensumFields.degrees: [duplicate.degrees.first().name],
                PensumFields.positions: [duplicate.positions.first().name],
                PensumFields.year_condition: NA,
                PensumFields.is_procedure_for_a_doctoral_degree_approved:
                    duplicate.is_procedure_for_a_doctoral_degree_approved,
                PensumFields.has_scholarship: NA,
            },
            'duplicate ' + PensumFields.has_scholarship: {
                **create_payload_data(),
                PensumFields.degrees: [duplicate.degrees.first().name],
                PensumFields.positions: [duplicate.positions.first().name],
                PensumFields.year_condition: NA,
                PensumFields.is_procedure_for_a_doctoral_degree_approved: NA,
                PensumFields.has_scholarship: duplicate.has_scholarship,
            }
        }

        cls.invalid_partial_data = {
            **cls.invalid_post_data_payload,
            'negative ' + PensumFields.value: {PensumFields.value: -1},
            'negative ' + PensumFields.limit: {PensumFields.limit: -1},
            f'{PensumFields.limit} lte {PensumFields.value}': {PensumFields.limit: cls.obj.value},
            f'{PensumFields.value} gte {PensumFields.limit}': {PensumFields.value: cls.obj.limit},
            'duplicate ' + PensumFields.degrees + '-' + PensumFields.positions: {
                PensumFields.degrees: [duplicate.degrees.first().name],
                PensumFields.positions: [duplicate.positions.first().name],
                PensumFields.year_condition: NA,
                PensumFields.is_procedure_for_a_doctoral_degree_approved: NA,
                PensumFields.has_scholarship: NA,
            },
            'duplicate ' + PensumFields.year_of_studies + ' and ' + PensumFields.year_condition: {
                PensumFields.degrees: [duplicate.degrees.first().name],
                PensumFields.positions: [duplicate.positions.first().name],
                PensumFields.year_of_studies: duplicate.year_of_studies,
                PensumFields.year_condition: duplicate.year_condition,
                PensumFields.is_procedure_for_a_doctoral_degree_approved: NA,
                PensumFields.has_scholarship: NA,
            },
            'duplicate ' + PensumFields.is_procedure_for_a_doctoral_degree_approved: {
                PensumFields.degrees: [duplicate.degrees.first().name],
                PensumFields.positions: [duplicate.positions.first().name],
                PensumFields.year_condition: NA,
                PensumFields.is_procedure_for_a_doctoral_degree_approved: duplicate.is_procedure_for_a_doctoral_degree_approved,
                PensumFields.has_scholarship: NA,
            },
            'duplicate ' + PensumFields.has_scholarship: {
                PensumFields.degrees: [duplicate.degrees.first().name],
                PensumFields.positions: [duplicate.positions.first().name],
                PensumFields.year_condition: NA,
                PensumFields.is_procedure_for_a_doctoral_degree_approved: NA,
                PensumFields.has_scholarship: duplicate.has_scholarship,
            }
        }
