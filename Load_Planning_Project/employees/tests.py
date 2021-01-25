import json
import random
import string

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APIRequestFactory, APITestCase
from .models import Degrees, Positions, Employees, Pensum
from .serializers import DegreeSerializer, PositionSerializer, EmployeeSerializer, PensumSerializer, \
    EmployeeListSerializer


class DegreesTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.factory = APIRequestFactory()

        cls.model = Degrees
        cls.serializer = DegreeSerializer
        cls.list_serializer = cls.serializer
        cls.basename = 'degrees'
        cls.context = {'request': cls.factory.get(reverse(cls.basename + '-list'), format=json)}
        cls.lookup = 'pk'
        cls.field_lookup = 'name'
        cls.delete_forbidden = True

        cls.obj_data = {cls.field_lookup: cls.get_random_field_str(cls.model, cls.field_lookup)}
        cls.obj = cls.model.objects.create(**cls.obj_data)
        for i in range(3):
            cls.model.objects.create(name=cls.get_random_field_str(cls.model, cls.field_lookup))

        cls.valid_post_data_payload = {
            'max length': {'name': cls.get_random_field_str(cls.model, cls.field_lookup)},
            'short': {'name': cls.get_random_str(1)},
        }

        cls.valid_put_data_payload = cls.valid_post_data_payload
        cls.valid_partial_data = cls.valid_post_data_payload

        cls.invalid_post_data_payload = {
            'over max length': {'name': cls.get_random_field_str(cls.model, cls.field_lookup) + 'x'},
            'empty string': {'name': ''},
        }

        cls.invalid_put_data_payload = cls.invalid_post_data_payload
        cls.invalid_partial_data = cls.invalid_post_data_payload

    @classmethod
    def get_random_str(cls, k):
        return ''.join(random.choices(string.ascii_letters, k=k))

    @classmethod
    def get_random_field_str(cls, model, field_name):
        return ''.join(random.choices(string.ascii_letters, k=getattr(model._meta.get_field(field_name), 'max_length')))

    def get_obj(self, data=None):
        """
        Try to return obj by data provided or just base self.obj if no data provided
        params data: (optional) raw dictionary data with field_lookup pointing record - if not provided: return self.obj
        return: model instance or None if not found
        """
        if data:
            try:
                return self.model.objects.get(**{self.field_lookup: data[self.field_lookup]})
            except ObjectDoesNotExist:
                return None
        else:
            return self.obj

    def get_obj_by_pk(self, pk):
        """
        Try to return obj by pk provided
        params pk: pk of the object
        return: model instance or None if not found
        """
        if pk:
            try:
                return self.model.objects.get(pk=pk)
            except ObjectDoesNotExist:
                return None
        return None

    def get_kwargs(self, obj=None, valid=True):
        """
        Get kwargs to build URL
        params obj: (optional) model instance - if not provided, self.obj is taken
        params valid: (optional) flag - return valid kwargs or not
        return: dictionary of URL kwargs
        """
        return {self.lookup: getattr((obj or self.obj), self.lookup)} if valid else {self.lookup: '99999'}

    def test_get_list_code(self):
        response = self.client.get(reverse(self.basename + '-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

    def test_get_list_data(self):
        response = self.client.get(reverse(self.basename + '-list'))
        self.assertJSONEqual(
            json.dumps(response.data),
            self.list_serializer(instance=self.model.objects.all(), many=True, context=self.context).data,
            response.data)

    def test_get_obj_code(self, obj=None, msg=None):
        response = self.client.get(reverse(self.basename + '-detail', kwargs=self.get_kwargs(obj)))
        self.assertEqual(response.status_code, status.HTTP_200_OK, (f"{msg}: " if msg else "") + f"{response.data}")

    def test_get_obj_data(self, obj=None, msg=None):
        response = self.client.get(reverse(self.basename + '-detail', kwargs=self.get_kwargs(obj)))
        self.assertJSONEqual(
            json.dumps(response.data), self.serializer(instance=(obj or self.obj), context=self.context).data,
            (f"{msg}: " if msg else "") + f"{response.data}")

    def test_post_data_payload_raw(self, payload_data=None):
        for msg, data in (payload_data or self.valid_post_data_payload).items():
            response = self.client.post(reverse(self.basename + '-list'), data=data)
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, (f"{msg}: " if msg else "") + f"{response.data}")
            # try to get created model instance
            obj = self.get_obj(data)
            self.assertIsNotNone(obj, msg)
            # check response code with get method
            self.test_get_obj_code(obj=obj, msg=msg)
            # check data integrity of data sent and serialized instance
            self.assertJSONEqual(
                json.dumps(response.data), self.serializer(instance=obj, context=self.context).data, msg)

    def test_post_data_payload_json(self, payload_data=None):
        for msg, data in (payload_data or self.valid_post_data_payload).items():
            response = self.client.post(
                reverse(self.basename + '-list'), data=json.dumps(data), content_type='application/json')
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, (f"{msg}: " if msg else "") + f"{response.data}")
            # try to get created model instance
            obj = self.get_obj(data)
            self.assertIsNotNone(obj, msg)
            # check response code with get method
            self.test_get_obj_code(obj=obj, msg=msg)
            # check data integrity of data sent and serialized instance
            self.assertJSONEqual(
                json.dumps(response.data), self.serializer(instance=obj, context=self.context).data, msg)

    def test_put_data_payload_raw(self, base_obj=None, payload_data=None):
        obj = base_obj
        for msg, data in (payload_data or self.valid_post_data_payload).items():
            response = self.client.put(reverse(self.basename + '-detail', kwargs=self.get_kwargs(obj)), data=data)
            self.assertEqual(response.status_code, status.HTTP_200_OK, (f"{msg}: " if msg else "") + f"{response.data}")
            # try to get updated model instance
            obj = self.get_obj(data)
            self.assertIsNotNone(obj, msg)
            self.assertEqual(obj.pk, self.obj.pk, msg)
            # check response code with get method
            self.test_get_obj_code(obj=obj, msg=msg)
            # check data integrity of data sent and serialized instance
            self.assertJSONEqual(
                json.dumps(response.data), self.serializer(instance=obj, context=self.context).data, msg)

    def test_put_data_payload_json(self, base_obj=None, payload_data=None):
        obj = base_obj
        for msg, data in (payload_data or self.valid_post_data_payload).items():
            response = self.client.put(
                reverse(self.basename + '-detail', kwargs=self.get_kwargs(obj)), data=json.dumps(data),
                content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_200_OK, (f"{msg}: " if msg else "") + f"{response.data}")
            # try to get updated model instance
            obj = self.get_obj(data)
            self.assertIsNotNone(obj, msg)
            self.assertEqual(obj.pk, self.obj.pk, msg)
            # check response code with get method
            self.test_get_obj_code(obj=obj, msg=msg)
            # check data integrity of data sent and serialized instance
            self.assertJSONEqual(
                json.dumps(response.data), self.serializer(instance=obj, context=self.context).data, msg)

    def test_patch_data_payload_raw(self, base_obj=None, payload_data=None):
        obj = base_obj
        for msg, data in (payload_data or self.valid_partial_data).items():
            response = self.client.patch(reverse(self.basename + '-detail', kwargs=self.get_kwargs(obj)), data=data)
            self.assertEqual(response.status_code, status.HTTP_200_OK, (f"{msg}: " if msg else "") + f"{response.data}")
            # try to get updated model instance
            obj = self.get_obj_by_pk(self.obj.pk)
            self.assertIsNotNone(obj, msg)
            # check response code with get method
            self.test_get_obj_code(obj=obj, msg=msg)
            # check data integrity of data sent and serialized instance
            self.assertJSONEqual(
                json.dumps(response.data), self.serializer(instance=obj, context=self.context).data, msg)

    def test_patch_data_payload_json(self, base_obj=None, payload_data=None):
        obj = base_obj
        for msg, data in (payload_data or self.valid_partial_data).items():
            response = self.client.patch(
                reverse(self.basename + '-detail', kwargs=self.get_kwargs(obj)), data=json.dumps(data),
                content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_200_OK, (f"{msg}: " if msg else "") + f"{response.data}")
            # try to get updated model instance
            obj = self.get_obj_by_pk(self.obj.pk)
            self.assertIsNotNone(obj, msg)
            # check response code with get method
            self.test_get_obj_code(obj=obj, msg=msg)
            # check data integrity of data sent and serialized instance
            self.assertJSONEqual(
                json.dumps(response.data), self.serializer(instance=obj, context=self.context).data, msg)

    def test_del_data(self, obj=None):
        response = self.client.delete(reverse(self.basename + '-detail', kwargs=self.get_kwargs(obj)))
        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED if self.delete_forbidden else status.HTTP_204_NO_CONTENT, response.data)
        # check if record has/hasn't been deleted
        if self.delete_forbidden:
            self.test_get_obj_code(obj)
        else:
            self.test_get_invalid(deleted_record=True)

    # INVALID DATA TESTS

    def test_get_invalid(self, deleted_record=False):
        response = self.client.get(reverse(self.basename + '-detail', kwargs=self.get_kwargs(valid=deleted_record)))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.data)

    def test_post_invalid_data_payload_raw(self, payload_data=None):
        records = [_.pk for _ in self.model.objects.all()]
        for msg, data in (payload_data or self.invalid_post_data_payload).items():
            response = self.client.post(reverse(self.basename + '-list'), data=data)
            self.assertEqual(
                response.status_code, status.HTTP_400_BAD_REQUEST, (f"{msg}: " if msg else "") + f"{response.data}")
            # double check records' pks
            self.assertEqual(records, [_.pk for _ in self.model.objects.all()])

    def test_post_invalid_data_payload_json(self, payload_data=None):
        records = [_.pk for _ in self.model.objects.all()]
        for msg, data in (payload_data or self.invalid_post_data_payload).items():
            response = self.client.post(
                reverse(self.basename + '-list'), data=json.dumps(data), content_type='application/json')
            self.assertEqual(
                response.status_code, status.HTTP_400_BAD_REQUEST, (f"{msg}: " if msg else "") + f"{response.data}")
            # double check records' pks
            self.assertEqual(records, [_.pk for _ in self.model.objects.all()])

    def test_put_invalid_data_payload_raw(self, base_obj=None, payload_data=None):
        for msg, data in (payload_data or self.invalid_put_data_payload).items():
            response = self.client.put(reverse(self.basename + '-detail', kwargs=self.get_kwargs(base_obj)), data=data)
            self.assertEqual(
                response.status_code, status.HTTP_400_BAD_REQUEST, (f"{msg}: " if msg else "") + f"{response.data}")
            # check if self.obj was not changed
            self.test_get_obj_data(obj=base_obj, msg=msg)

    def test_put_invalid_data_payload_json(self, base_obj=None, payload_data=None):
        for msg, data in (payload_data or self.invalid_put_data_payload).items():
            response = self.client.put(
                reverse(self.basename + '-detail', kwargs=self.get_kwargs(base_obj)), data=json.dumps(data),
                content_type='application/json')
            self.assertEqual(
                response.status_code, status.HTTP_400_BAD_REQUEST, (f"{msg}: " if msg else "") + f"{response.data}")
            # check if self.obj was not changed
            self.test_get_obj_data(obj=base_obj, msg=msg)

    def test_patch_invalid_data_payload_raw(self, base_obj=None, payload_data=None):
        for msg, data in (payload_data or self.invalid_partial_data).items():
            response = self.client.patch(
                reverse(self.basename + '-detail', kwargs=self.get_kwargs(base_obj)), data=data)
            self.assertEqual(
                response.status_code, status.HTTP_400_BAD_REQUEST, (f"{msg}: " if msg else "") + f"{response.data}")
            # check if self.obj was not changed
            self.test_get_obj_data(obj=base_obj, msg=msg)

    def test_patch_invalid_data_payload_json(self, base_obj=None, payload_data=None):
        for msg, data in (payload_data or self.invalid_partial_data).items():
            response = self.client.patch(
                reverse(self.basename + '-detail', kwargs=self.get_kwargs(base_obj)), data=json.dumps(data),
                content_type='application/json')
            self.assertEqual(
                response.status_code, status.HTTP_400_BAD_REQUEST, (f"{msg}: " if msg else "") + f"{response.data}")
            # check if self.obj was not changed
            self.test_get_obj_data(obj=base_obj, msg=msg)

    def test_del_invalid_data(self):
        response = self.client.delete(reverse(self.basename + '-detail', kwargs=self.get_kwargs(valid=False)))
        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED if self.delete_forbidden else status.HTTP_404_NOT_FOUND, response.data)


class PositionsTests(DegreesTests):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.factory = APIRequestFactory()

        cls.model = Positions
        cls.serializer = PositionSerializer
        cls.list_serializer = cls.serializer
        cls.basename = 'positions'
        cls.context = {'request': cls.factory.get(reverse(cls.basename + '-list'), format=json)}
        cls.lookup = 'pk'
        cls.field_lookup = 'name'
        cls.delete_forbidden = True

        cls.obj_data = {cls.field_lookup: cls.get_random_field_str(cls.model, cls.field_lookup)}
        cls.obj = cls.model.objects.create(**cls.obj_data)
        for i in range(3):
            cls.model.objects.create(name=cls.get_random_field_str(cls.model, cls.field_lookup))

        cls.valid_post_data_payload = {
            'max length': {'name': cls.get_random_field_str(cls.model, cls.field_lookup)},
            'short': {'name': cls.get_random_str(1)},
        }

        cls.valid_put_data_payload = cls.valid_post_data_payload
        cls.valid_partial_data = cls.valid_post_data_payload

        cls.invalid_post_data_payload = {
            'over max length': {'name': cls.get_random_field_str(cls.model, cls.field_lookup) + 'x'},
            'empty string': {'name': ''},
        }

        cls.invalid_put_data_payload = cls.invalid_post_data_payload
        cls.invalid_partial_data = cls.invalid_post_data_payload


class EmployeesTests(DegreesTests):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.factory = APIRequestFactory()

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

        cls.model = Employees
        cls.serializer = EmployeeSerializer
        cls.list_serializer = EmployeeListSerializer
        cls.basename = 'employees'
        cls.context = {'request': cls.factory.get(reverse(cls.basename + '-list'), format=json)}
        cls.lookup = abbreviation
        cls.field_lookup = cls.lookup
        cls.delete_forbidden = False

        def create_model_data():
            return {
                first_name: cls.get_random_field_str(cls.model, first_name),
                last_name: cls.get_random_field_str(cls.model, last_name),
                abbreviation: cls.get_random_field_str(cls.model, abbreviation),
                e_mail: cls.get_random_field_str(cls.model, e_mail)[:-6] + '@ab.ba',
                degree: Degrees.objects.create(name=cls.get_random_str(5)),
                position: Positions.objects.create(name=cls.get_random_str(5))
            }

        cls.obj = cls.model.objects.create(**create_model_data())
        for i in range(3):
            cls.model.objects.create(**create_model_data())

        def create_payload_data():
            return {
                first_name: cls.get_random_field_str(cls.model, first_name),
                last_name: cls.get_random_field_str(cls.model, last_name),
                abbreviation: cls.get_random_field_str(cls.model, abbreviation),
                e_mail: cls.get_random_field_str(cls.model, e_mail)[:-6] + '@ab.ba',
                degree: Degrees.objects.create(name=cls.get_random_str(5)).name,
                position: Positions.objects.create(name=cls.get_random_str(5)).name,
                'supervisor': None,
            }

        cls.valid_post_data_payload = {
            'max length': create_payload_data(),
            'short strings': {
                first_name: cls.get_random_str(1),
                last_name: cls.get_random_str(1),
                abbreviation: cls.get_random_str(1),
                e_mail: cls.get_random_str(1) + '@ab.ba',
                degree: Degrees.objects.create(name=cls.get_random_str(5)).name,
                position: Positions.objects.create(name=cls.get_random_str(5)).name,
                supervisor: None,
            },
            'all fields': {
                **create_payload_data(),
                supervisor: Employees.objects.create(**create_model_data()).abbreviation,
                year_of_studies: random.randint(1, 100),
                is_procedure_for_a_doctoral_degree_approved: random.choices([True, False])[0],
                has_scholarship: random.choices([True, False])[0],
            }
        }
        
        cls.valid_put_data_payload = cls.valid_post_data_payload
        
        cls.valid_partial_data = {
            'max length ' + first_name: {first_name: cls.get_random_field_str(cls.model, first_name)}
        }

        rand_abbreviation = cls.get_random_field_str(cls.model, abbreviation)
        cls.invalid_post_data_payload = {
            'empty ' + first_name: {**create_payload_data(), first_name: ''},
            'self supervising with new abbreviation': {
                **create_payload_data(), 'abbreviation': rand_abbreviation, 'supervisor': rand_abbreviation}
        }

        cls.invalid_put_data_payload = {
            **cls.invalid_post_data_payload,
            'self supervising with old abbreviation': {
                **create_payload_data(), 'abbreviation': cls.obj.abbreviation, 'supervisor': cls.obj.abbreviation
            }
        }
        for field in (first_name, last_name, abbreviation, e_mail):
            cls.invalid_partial_data['empty ' + field] = {**create_payload_data(), field: ''}
            cls.invalid_partial_data['too long ' + field] = {
                **create_payload_data(),
                field: cls.get_random_field_str(cls.model, first_name) + cls.get_random_str(1)}

        cls.invalid_partial_data = {
            'self supervising': {'supervisor': cls.obj.abbreviation}}
        for field in (first_name, last_name, abbreviation, e_mail):
            cls.invalid_partial_data['empty ' + field] = {field: ''}
            cls.invalid_partial_data['too long ' + field] = {
                field: cls.get_random_field_str(cls.model, first_name) + cls.get_random_str(1)}


class PensumTests(DegreesTests):
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
        cls.basename = 'pensum'
        cls.context = {'request': cls.factory.get(reverse(cls.basename + '-list'), format=json)}
        cls.lookup = 'pk'
        cls.field_lookup = name
        cls.delete_forbidden = False

        def create_model_data():
            return {
                name: cls.get_random_field_str(cls.model, name),
                value: random.randint(1, 500),
                limit: random.randint(501, 1000),
            }

        cls.obj = cls.model.objects.create(**create_model_data())
        cls.obj.degrees.create(name=cls.get_random_str(15))
        cls.obj.positions.create(name=cls.get_random_str(15))
        cls.obj.degrees.create(name=cls.get_random_str(15))
        cls.obj.positions.create(name=cls.get_random_str(15))
        for i in range(3):
            pensum = cls.model.objects.create(**create_model_data())
            pensum.degrees.create(name=cls.get_random_str(15))
            pensum.positions.create(name=cls.get_random_str(15))
            pensum.degrees.create(name=cls.get_random_str(15))
            pensum.positions.create(name=cls.get_random_str(15))

        duplicate = cls.model.objects.create(**{
            **create_model_data(),
            year_of_studies: random.randint(1, 20),
            year_condition: random.choices(Pensum.YEAR_CONDITION_CHOICES)[0][0],
            is_procedure_for_a_doctoral_degree_approved: random.choices(Pensum.DOCTORAL_PROCEDURE_CHOICES)[0][0],
            has_scholarship: random.choices(Pensum.SCHOLARSHIP_CHOICES)[0][0],
        })
        duplicate.degrees.create(name=cls.get_random_str(15))
        duplicate.positions.create(name=cls.get_random_str(15))

        def create_payload_data():
            return {
                name: cls.get_random_field_str(cls.model, name),
                value: random.randint(1, 500),
                limit: random.randint(501, 1000),
                degrees: [
                    Degrees.objects.create(name=cls.get_random_str(15)).name,
                    Degrees.objects.create(name=cls.get_random_str(15)).name
                ],
                positions: [
                    Positions.objects.create(name=cls.get_random_str(15)).name,
                    Positions.objects.create(name=cls.get_random_str(15)).name
                ],
            }

        cls.valid_post_data_payload = {
            'max length': {**create_payload_data()},
            'short': {**create_payload_data(), 'name': cls.get_random_str(1)},
            'same ' + degrees + ' & ' + positions + ' but different ' + year_condition + ' & ' + year_of_studies: {
                **create_payload_data(),
                degrees: [_.name for _ in cls.obj.degrees.all()],
                positions: [_.name for _ in cls.obj.positions.all()],
                year_of_studies: random.randint(1, 20),
                year_condition: random.choices(Pensum.YEAR_CONDITION_CHOICES)[0][0],
            },
            'completed data': {
                **create_payload_data(),
                year_of_studies: random.randint(1, 20),
                year_condition: random.choices(Pensum.YEAR_CONDITION_CHOICES)[0][0],
                is_procedure_for_a_doctoral_degree_approved: random.choices(Pensum.DOCTORAL_PROCEDURE_CHOICES)[0][0],
                has_scholarship: random.choices(Pensum.SCHOLARSHIP_CHOICES)[0][0]
            }
        }

        cls.valid_put_data_payload = cls.valid_post_data_payload

        cls.valid_partial_data = {
            'max length ' + name: {name: cls.get_random_field_str(cls.model, name)},
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
                name: cls.get_random_field_str(cls.model, name) + cls.get_random_str(1)},
            'empty ' + name: {**create_payload_data(), name: ''},
            'duplicate ' + degrees + '-' + positions: {
                **create_payload_data(),
                degrees: [cls.obj.degrees.first().name],
                positions: [cls.obj.positions.first().name]
            },
            'duplicate ' + year_of_studies + ' and ' + year_condition: {
                **create_payload_data(),
                degrees: [cls.obj.degrees.first().name],
                positions: [cls.obj.positions.first().name],
                year_of_studies: cls.obj.year_of_studies,
                year_condition: cls.obj.year_condition,
            }
        }

        cls.invalid_put_data_payload = {
            'duplicate ' + degrees + '-' + positions: {
                **create_payload_data(),
                degrees: [duplicate.degrees.first().name],
                positions: [duplicate.positions.first().name]
            },
            'duplicate ' + year_of_studies + ' and ' + year_condition: {
                **create_payload_data(),
                degrees: [duplicate.degrees.first().name],
                positions: [duplicate.positions.first().name],
                year_of_studies: duplicate.year_of_studies,
                year_condition: duplicate.year_condition,
            },
            'duplicate ' + is_procedure_for_a_doctoral_degree_approved: {
                **create_payload_data(),
                degrees: [duplicate.degrees.first().name],
                positions: [duplicate.positions.first().name],
                is_procedure_for_a_doctoral_degree_approved: duplicate.is_procedure_for_a_doctoral_degree_approved,
            },
            'duplicate ' + has_scholarship: {
                **create_payload_data(),
                degrees: [duplicate.degrees.first().name],
                positions: [duplicate.positions.first().name],
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
            },
            'duplicate ' + year_of_studies + ' and ' + year_condition: {
                degrees: [duplicate.degrees.first().name],
                positions: [duplicate.positions.first().name],
                year_of_studies: duplicate.year_of_studies,
                year_condition: duplicate.year_condition,
            },
            'duplicate ' + is_procedure_for_a_doctoral_degree_approved: {
                degrees: [duplicate.degrees.first().name],
                positions: [duplicate.positions.first().name],
                is_procedure_for_a_doctoral_degree_approved: duplicate.is_procedure_for_a_doctoral_degree_approved,
            },
            'duplicate ' + has_scholarship: {
                degrees: [duplicate.degrees.first().name],
                positions: [duplicate.positions.first().name],
                has_scholarship: duplicate.is_procedure_for_a_doctoral_degree_approved,
            }
        }
