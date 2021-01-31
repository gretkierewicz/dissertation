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


class EmpFields:
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
        cls.field_lookup = 'name'
        cls.delete_forbidden = True

        cls.obj_data = {cls.field_lookup: random_max_len_field_str(cls.model, cls.field_lookup)}
        cls.obj = cls.model.objects.create(**cls.obj_data)
        for i in range(3):
            cls.model.objects.create(name=random_max_len_field_str(cls.model, cls.field_lookup))

        cls.valid_post_data_payload = {
            'max length': {'name': random_max_len_field_str(cls.model, cls.field_lookup)},
            'short': {'name': random_str(1)},
        }

        cls.valid_put_data_payload = cls.valid_post_data_payload
        cls.valid_partial_data = cls.valid_post_data_payload

        cls.invalid_post_data_payload = {
            'over max length': {'name': random_max_len_field_str(cls.model, cls.field_lookup) + 'x'},
            'empty string': {'name': ''},
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
        cls.field_lookup = 'name'
        cls.delete_forbidden = True

        cls.obj_data = {cls.field_lookup: random_max_len_field_str(cls.model, cls.field_lookup)}
        cls.obj = cls.model.objects.create(**cls.obj_data)
        for i in range(3):
            cls.model.objects.create(name=random_max_len_field_str(cls.model, cls.field_lookup))

        cls.valid_post_data_payload = {
            'max length': {'name': random_max_len_field_str(cls.model, cls.field_lookup)},
            'short': {'name': random_str(1)},
        }

        cls.valid_put_data_payload = cls.valid_post_data_payload
        cls.valid_partial_data = cls.valid_post_data_payload

        cls.invalid_post_data_payload = {
            'over max length': {'name': random_max_len_field_str(cls.model, cls.field_lookup) + 'x'},
            'empty string': {'name': ''},
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
        cls.lookup = EmpFields.abbreviation
        cls.field_lookup = cls.lookup
        cls.delete_forbidden = False

        def create_model_data():
            return {
                EmpFields.first_name: random_max_len_field_str(cls.model, EmpFields.first_name),
                EmpFields.last_name: random_max_len_field_str(cls.model, EmpFields.last_name),
                EmpFields.abbreviation: random_max_len_field_str(cls.model, EmpFields.abbreviation),
                EmpFields.e_mail: random_max_len_field_str(cls.model, EmpFields.e_mail)[:-6] + '@ab.ba',
                EmpFields.degree: Degrees.objects.create(name=random_str(5)),
                EmpFields.position: Positions.objects.create(name=random_str(5))
            }

        cls.obj = cls.model.objects.create(**create_model_data())
        for i in range(3):
            cls.model.objects.create(**create_model_data())

        def create_payload_data():
            return {
                EmpFields.first_name: random_max_len_field_str(cls.model, EmpFields.first_name),
                EmpFields.last_name: random_max_len_field_str(cls.model, EmpFields.last_name),
                EmpFields.abbreviation: random_max_len_field_str(cls.model, EmpFields.abbreviation),
                EmpFields.e_mail: random_max_len_field_str(cls.model, EmpFields.e_mail)[:-6] + '@ab.ba',
                EmpFields.degree: Degrees.objects.create(name=random_str(5)).name,
                EmpFields.position: Positions.objects.create(name=random_str(5)).name,
                'supervisor': None,
            }

        cls.valid_post_data_payload = {
            'max length': create_payload_data(),
            'short strings': {
                EmpFields.first_name: random_str(1),
                EmpFields.last_name: random_str(1),
                EmpFields.abbreviation: random_str(1),
                EmpFields.e_mail: random_str(1) + '@ab.ba',
                EmpFields.degree: Degrees.objects.create(name=random_str(5)).name,
                EmpFields.position: Positions.objects.create(name=random_str(5)).name,
                EmpFields.supervisor: None,
            },
            'all fields': {
                **create_payload_data(),
                EmpFields.supervisor: Employees.objects.create(**create_model_data()).abbreviation,
                EmpFields.year_of_studies: random.randint(1, 100),
                EmpFields.is_procedure_for_a_doctoral_degree_approved: random_bool(),
                EmpFields.has_scholarship: random_bool(),
            }
        }
        
        cls.valid_put_data_payload = cls.valid_post_data_payload
        
        cls.valid_partial_data = {
            'max length ' + EmpFields.first_name: {
                EmpFields.first_name: random_max_len_field_str(cls.model, EmpFields.first_name)
            }
        }

        rand_abbreviation = random_max_len_field_str(cls.model, EmpFields.abbreviation)
        cls.invalid_post_data_payload = {
            'empty ' + EmpFields.first_name: {**create_payload_data(), EmpFields.first_name: ''},
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
        for field in EmpFields.string_fields:
            cls.invalid_partial_data['empty ' + field] = {**create_payload_data(), field: ''}
            cls.invalid_partial_data['too long ' + field] = {
                **create_payload_data(),
                field: random_max_len_field_str(cls.model, EmpFields.first_name) + random_str(1)}

        cls.invalid_partial_data = {
            'self supervising': {'supervisor': cls.obj.abbreviation}}
        for field in EmpFields.string_fields:
            cls.invalid_partial_data['empty ' + field] = {field: ''}
            cls.invalid_partial_data['too long ' + field] = {
                field: random_max_len_field_str(cls.model, EmpFields.first_name) + random_str(1)}


class PensumTests(BasicAPITests, APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.factory = APIRequestFactory()

        name = 'name'
        value = 'value'
        limit = 'limit'
        degrees = 'degrees'
        positions = 'positions'
        year_of_studies = 'year_of_studies'
        year_condition = 'year_condition'
        is_procedure_for_a_doctoral_degree_approved = 'is_procedure_for_a_doctoral_degree_approved'
        has_scholarship = 'has_scholarship'

        cls.model = Pensum
        cls.serializer = PensumSerializer
        cls.list_serializer = cls.serializer
        cls.list_view_name = 'pensum-list'
        cls.detail_view_name = 'pensum-detail'
        cls.context = {'request': cls.factory.get(reverse(cls.list_view_name), format=json)}
        cls.lookup = 'pk'
        cls.field_lookup = name
        cls.delete_forbidden = False

        def create_model_data():
            return {
                name: random_max_len_field_str(cls.model, name),
                value: random.randint(1, 500),
                limit: random.randint(501, 1000),
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
            year_of_studies: random.randint(1, 20),
            year_condition: random.choice(active_year_choices),
            is_procedure_for_a_doctoral_degree_approved: random.choice(active_procedure_choices),
            has_scholarship: random.choice(active_scholarship_choices),
        })
        duplicate.degrees.create(name=random_str(15))
        duplicate.positions.create(name=random_str(15))

        def create_payload_data():
            return {
                name: random_max_len_field_str(cls.model, name),
                value: random.randint(1, 500),
                limit: random.randint(501, 1000),
                degrees: [
                    Degrees.objects.create(name=random_str(15)).name,
                    Degrees.objects.create(name=random_str(15)).name
                ],
                positions: [
                    Positions.objects.create(name=random_str(15)).name,
                    Positions.objects.create(name=random_str(15)).name
                ],
            }

        cls.valid_post_data_payload = {
            'max length': {**create_payload_data()},
            'short': {**create_payload_data(), 'name': random_str(1)},
            'same ' + degrees + ' & ' + positions + ' but different ' + year_condition + ' & ' + year_of_studies: {
                **create_payload_data(),
                degrees: [_.name for _ in cls.obj.degrees.all()],
                positions: [_.name for _ in cls.obj.positions.all()],
                year_of_studies: random.randint(1, 20),
                year_condition: random.choice(active_year_choices),
                is_procedure_for_a_doctoral_degree_approved: NA,
                has_scholarship: NA,
            },
            'completed data': {
                **create_payload_data(),
                year_of_studies: random.randint(1, 20),
                year_condition: random.choice(active_year_choices),
                is_procedure_for_a_doctoral_degree_approved: random.choice(active_procedure_choices),
                has_scholarship: random.choice(active_scholarship_choices),
            }
        }

        cls.valid_put_data_payload = cls.valid_post_data_payload

        cls.valid_partial_data = {
            'max length ' + name: {name: random_max_len_field_str(cls.model, name)},
            'min ' + value: {value: 0},
            'min ' + limit: {limit: 1},
            'high ' + limit: {limit: 2000},
            'high ' + value: {value: 1999},
            'no ' + limit: {limit: None},
            'rand ' + value: {value: 333},
            'min ' + limit: {limit: 334},
        }

        cls.invalid_post_data_payload = {
            'too long ' + name: {
                **create_payload_data(),
                name: random_max_len_field_str(cls.model, name) + random_str(1)},
            'empty ' + name: {**create_payload_data(), name: ''},
            'duplicate ' + degrees + '-' + positions: {
                **create_payload_data(),
                degrees: [cls.obj.degrees.first().name],
                positions: [cls.obj.positions.first().name],
                year_condition: NA,
                is_procedure_for_a_doctoral_degree_approved: NA,
                has_scholarship: NA,
            },
            'duplicate ' + year_of_studies + ' and ' + year_condition: {
                **create_payload_data(),
                degrees: [cls.obj.degrees.first().name],
                positions: [cls.obj.positions.first().name],
                year_of_studies: cls.obj.year_of_studies,
                year_condition: cls.obj.year_condition,
                is_procedure_for_a_doctoral_degree_approved: NA,
                has_scholarship: NA,
            }
        }

        cls.invalid_put_data_payload = {
            'duplicate ' + degrees + '-' + positions: {
                **create_payload_data(),
                degrees: [duplicate.degrees.first().name],
                positions: [duplicate.positions.first().name],
                year_condition: NA,
                is_procedure_for_a_doctoral_degree_approved: NA,
                has_scholarship: NA,
            },
            'duplicate ' + year_of_studies + ' and ' + year_condition: {
                **create_payload_data(),
                degrees: [duplicate.degrees.first().name],
                positions: [duplicate.positions.first().name],
                year_of_studies: duplicate.year_of_studies,
                year_condition: duplicate.year_condition,
                is_procedure_for_a_doctoral_degree_approved: NA,
                has_scholarship: NA,
            },
            'duplicate ' + is_procedure_for_a_doctoral_degree_approved: {
                **create_payload_data(),
                degrees: [duplicate.degrees.first().name],
                positions: [duplicate.positions.first().name],
                year_condition: NA,
                is_procedure_for_a_doctoral_degree_approved: duplicate.is_procedure_for_a_doctoral_degree_approved,
                has_scholarship: NA,
            },
            'duplicate ' + has_scholarship: {
                **create_payload_data(),
                degrees: [duplicate.degrees.first().name],
                positions: [duplicate.positions.first().name],
                year_condition: NA,
                is_procedure_for_a_doctoral_degree_approved: NA,
                has_scholarship: duplicate.has_scholarship,
            }
        }

        cls.invalid_partial_data = {
            **cls.invalid_post_data_payload,
            'negative ' + value: {value: -1},
            'negative ' + limit: {limit: -1},
            'limit lte value': {limit: cls.obj.value},
            'value gte limit': {value: cls.obj.limit},
            'duplicate ' + degrees + '-' + positions: {
                degrees: [duplicate.degrees.first().name],
                positions: [duplicate.positions.first().name],
                year_condition: NA,
                is_procedure_for_a_doctoral_degree_approved: NA,
                has_scholarship: NA,
            },
            'duplicate ' + year_of_studies + ' and ' + year_condition: {
                degrees: [duplicate.degrees.first().name],
                positions: [duplicate.positions.first().name],
                year_of_studies: duplicate.year_of_studies,
                year_condition: duplicate.year_condition,
                is_procedure_for_a_doctoral_degree_approved: NA,
                has_scholarship: NA,
            },
            'duplicate ' + is_procedure_for_a_doctoral_degree_approved: {
                degrees: [duplicate.degrees.first().name],
                positions: [duplicate.positions.first().name],
                year_condition: NA,
                is_procedure_for_a_doctoral_degree_approved: duplicate.is_procedure_for_a_doctoral_degree_approved,
                has_scholarship: NA,
            },
            'duplicate ' + has_scholarship: {
                degrees: [duplicate.degrees.first().name],
                positions: [duplicate.positions.first().name],
                year_condition: NA,
                is_procedure_for_a_doctoral_degree_approved: NA,
                has_scholarship: duplicate.has_scholarship,
            }
        }
