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

        cls.data_payload = {
            'max length': {'name': cls.get_random_field_str(cls.model, cls.field_lookup)},
            'short': {'name': cls.get_random_str(1)},
        }
        cls.partial_data = cls.data_payload

        cls.invalid_data_payload = {
            'over max length': {'name': cls.get_random_field_str(cls.model, cls.field_lookup) + 'x'},
            'empty string': {'name': ''},
        }
        cls.invalid_partial_data = cls.invalid_data_payload

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
        obj = obj if obj else self.obj
        return {self.lookup: getattr(obj, self.lookup)} if valid else {self.lookup: '99999'}

    def test_get_list_code(self):
        response = self.client.get(reverse(self.basename + '-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

    def test_get_list_data(self):
        response = self.client.get(reverse(self.basename + '-list'))
        self.assertJSONEqual(
            json.dumps(response.data),
            self.list_serializer(instance=self.model.objects.all(), many=True, context=self.context).data,
            response.data)

    def test_get_obj_code(self, obj=None, key=None):
        response = self.client.get(reverse(self.basename + '-detail', kwargs=self.get_kwargs(obj)))
        self.assertEqual(response.status_code, status.HTTP_200_OK, (f"{key}: " if key else "") + f"{response.data}")

    def test_get_obj_data(self, key=None):
        response = self.client.get(reverse(self.basename + '-detail', kwargs=self.get_kwargs()))
        self.assertJSONEqual(
            json.dumps(response.data), self.serializer(instance=self.obj, context=self.context).data,
            (f"{key}: " if key else "") + f"{response.data}")

    def test_post_data_payload_raw(self):
        for key, data in self.data_payload.items():
            response = self.client.post(reverse(self.basename + '-list'), data=data)
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, (f"{key}: " if key else "") + f"{response.data}")
            # try to get created model instance
            obj = self.get_obj(data)
            self.assertIsNotNone(obj, key)
            # check response code with get method
            self.test_get_obj_code(obj=obj, key=key)
            # check data integrity of data sent and serialized instance
            self.assertJSONEqual(
                json.dumps(response.data), self.serializer(instance=obj, context=self.context).data, key)

    def test_post_data_payload_json(self):
        for key, data in self.data_payload.items():
            response = self.client.post(
                reverse(self.basename + '-list'), data=json.dumps(data), content_type='application/json')
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, (f"{key}: " if key else "") + f"{response.data}")
            # try to get created model instance
            obj = self.get_obj(data)
            self.assertIsNotNone(obj, key)
            # check response code with get method
            self.test_get_obj_code(obj=obj, key=key)
            # check data integrity of data sent and serialized instance
            self.assertJSONEqual(
                json.dumps(response.data), self.serializer(instance=obj, context=self.context).data, key)

    def test_put_data_payload_raw(self):
        for key, data in self.data_payload.items():
            response = self.client.put(reverse(self.basename + '-detail', kwargs=self.get_kwargs()), data=data)
            self.assertEqual(response.status_code, status.HTTP_200_OK, (f"{key}: " if key else "") + f"{response.data}")
            # try to get updated model instance
            obj = self.get_obj(data)
            self.assertIsNotNone(obj, key)
            self.assertEqual(obj.pk, self.obj.pk, key)
            # check response code with get method
            self.test_get_obj_code(obj=obj, key=key)
            # check data integrity of data sent and serialized instance
            self.assertJSONEqual(
                json.dumps(response.data), self.serializer(instance=obj, context=self.context).data, key)

    def test_put_data_payload_json(self):
        for key, data in self.data_payload.items():
            response = self.client.put(
                reverse(self.basename + '-detail', kwargs=self.get_kwargs()), data=json.dumps(data),
                content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_200_OK, (f"{key}: " if key else "") + f"{response.data}")
            # try to get updated model instance
            obj = self.get_obj(data)
            self.assertIsNotNone(obj, key)
            self.assertEqual(obj.pk, self.obj.pk, key)
            # check response code with get method
            self.test_get_obj_code(obj=obj, key=key)
            # check data integrity of data sent and serialized instance
            self.assertJSONEqual(
                json.dumps(response.data), self.serializer(instance=obj, context=self.context).data, key)

    def test_patch_data_payload_raw(self):
        for key, data in self.partial_data.items():
            response = self.client.patch(reverse(self.basename + '-detail', kwargs=self.get_kwargs()), data=data)
            self.assertEqual(response.status_code, status.HTTP_200_OK, (f"{key}: " if key else "") + f"{response.data}")
            # try to get updated model instance
            obj = self.get_obj_by_pk(self.obj.pk)
            self.assertIsNotNone(obj, key)
            # check response code with get method
            self.test_get_obj_code(obj=obj, key=key)
            # check data integrity of data sent and serialized instance
            self.assertJSONEqual(
                json.dumps(response.data), self.serializer(instance=obj, context=self.context).data, key)

    def test_patch_data_payload_json(self):
        for key, data in self.partial_data.items():
            response = self.client.patch(
                reverse(self.basename + '-detail', kwargs=self.get_kwargs()), data=json.dumps(data),
                content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_200_OK, (f"{key}: " if key else "") + f"{response.data}")
            # try to get updated model instance
            obj = self.get_obj_by_pk(self.obj.pk)
            self.assertIsNotNone(obj, key)
            # check response code with get method
            self.test_get_obj_code(obj=obj, key=key)
            # check data integrity of data sent and serialized instance
            self.assertJSONEqual(
                json.dumps(response.data), self.serializer(instance=obj, context=self.context).data, key)

    def test_del_data(self):
        response = self.client.delete(reverse(self.basename + '-detail', kwargs=self.get_kwargs()))
        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED if self.delete_forbidden else status.HTTP_204_NO_CONTENT, response.data)
        # check if record has/hasn't been deleted
        if self.delete_forbidden:
            self.test_get_obj_code()
        else:
            self.test_get_invalid(deleted_record=True)

    # INVALID DATA TESTS

    def test_get_invalid(self, deleted_record=False):
        response = self.client.get(reverse(self.basename + '-detail', kwargs=self.get_kwargs(valid=deleted_record)))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.data)

    def test_post_invalid_data_payload_raw(self):
        records = [_.pk for _ in self.model.objects.all()]
        for key, data in self.invalid_data_payload.items():
            response = self.client.post(reverse(self.basename + '-list'), data=data)
            self.assertEqual(
                response.status_code, status.HTTP_400_BAD_REQUEST, (f"{key}: " if key else "") + f"{response.data}")
            # check if not created
            obj = self.get_obj(data)
            self.assertIsNone(obj, key)
            # double check records' pks
            self.assertEqual(records, [_.pk for _ in self.model.objects.all()])

    def test_post_invalid_data_payload_json(self):
        records = [_.pk for _ in self.model.objects.all()]
        for key, data in self.invalid_data_payload.items():
            response = self.client.post(
                reverse(self.basename + '-list'), data=json.dumps(data), content_type='application/json')
            self.assertEqual(
                response.status_code, status.HTTP_400_BAD_REQUEST, (f"{key}: " if key else "") + f"{response.data}")
            # check if not created
            obj = self.get_obj(data)
            self.assertIsNone(obj, key)
            # double check records' pks
            self.assertEqual(records, [_.pk for _ in self.model.objects.all()])

    def test_put_invalid_data_payload_raw(self):
        for key, data in self.invalid_data_payload.items():
            response = self.client.put(reverse(self.basename + '-detail', kwargs=self.get_kwargs()), data=data)
            self.assertEqual(
                response.status_code, status.HTTP_400_BAD_REQUEST, (f"{key}: " if key else "") + f"{response.data}")
            # check if self.obj was not changed
            self.test_get_obj_data(key=key)

    def test_put_invalid_data_payload_json(self):
        for key, data in self.invalid_data_payload.items():
            response = self.client.put(
                reverse(self.basename + '-detail', kwargs=self.get_kwargs()), data=json.dumps(data),
                content_type='application/json')
            self.assertEqual(
                response.status_code, status.HTTP_400_BAD_REQUEST, (f"{key}: " if key else "") + f"{response.data}")
            # check if self.obj was not changed
            self.test_get_obj_data(key=key)

    def test_patch_invalid_data_payload_raw(self):
        for key, data in self.invalid_partial_data.items():
            response = self.client.patch(reverse(self.basename + '-detail', kwargs=self.get_kwargs()), data=data)
            self.assertEqual(
                response.status_code, status.HTTP_400_BAD_REQUEST, (f"{key}: " if key else "") + f"{response.data}")
            # check if self.obj was not changed
            self.test_get_obj_data(key=key)

    def test_patch_invalid_data_payload_json(self):
        for key, data in self.invalid_partial_data.items():
            response = self.client.patch(
                reverse(self.basename + '-detail', kwargs=self.get_kwargs()), data=json.dumps(data),
                content_type='application/json')
            self.assertEqual(
                response.status_code, status.HTTP_400_BAD_REQUEST, (f"{key}: " if key else "") + f"{response.data}")
            # check if self.obj was not changed
            self.test_get_obj_data(key=key)

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

        cls.data_payload = {
            'max length': {'name': cls.get_random_field_str(cls.model, cls.field_lookup)},
            'short': {'name': cls.get_random_str(1)},
        }
        cls.partial_data = cls.data_payload

        cls.invalid_data_payload = {
            'over max length': {'name': cls.get_random_field_str(cls.model, cls.field_lookup) + 'x'},
            'empty string': {'name': ''},
        }
        cls.invalid_partial_data = cls.invalid_data_payload


class EmployeesTests(DegreesTests):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.factory = APIRequestFactory()

        cls.model = Employees
        cls.serializer = EmployeeSerializer
        cls.list_serializer = EmployeeListSerializer
        cls.basename = 'employees'
        cls.context = {'request': cls.factory.get(reverse(cls.basename + '-list'), format=json)}
        cls.lookup = 'abbreviation'
        cls.field_lookup = 'abbreviation'
        cls.delete_forbidden = False

        cls.obj = cls.model.objects.create(**{
                'first_name': cls.get_random_field_str(cls.model, 'first_name'),
                'last_name': cls.get_random_field_str(cls.model, 'last_name'),
                cls.field_lookup: cls.get_random_field_str(cls.model, cls.field_lookup),
                'e_mail': cls.get_random_field_str(cls.model, 'e_mail')[:-6] + '@ab.ba',
                'degree': Degrees.objects.create(name=cls.get_random_str(5)),
                'position': Positions.objects.create(name=cls.get_random_str(5))
            })
        for i in range(0):
            cls.model.objects.create(**{
                'first_name': cls.get_random_field_str(cls.model, 'first_name'),
                'last_name': cls.get_random_field_str(cls.model, 'last_name'),
                cls.field_lookup: cls.get_random_field_str(cls.model, cls.field_lookup),
                'e_mail': cls.get_random_field_str(cls.model, 'e_mail')[:-6] + '@ab.ba',
                'degree': Degrees.objects.create(name=cls.get_random_str(5)),
                'position': Positions.objects.create(name=cls.get_random_str(5))
            })

        def create_simple_data():
            return {
                'first_name': cls.get_random_field_str(cls.model, 'first_name'),
                'last_name': cls.get_random_field_str(cls.model, 'last_name'),
                'abbreviation': cls.get_random_field_str(cls.model, 'abbreviation'),
                'e_mail': cls.get_random_field_str(cls.model, 'e_mail')[:-6] + '@ab.ba',
                'degree': Degrees.objects.create(name=cls.get_random_str(5)).name,
                'position': Positions.objects.create(name=cls.get_random_str(5)).name,
                'supervisor': None,
            }

        cls.data_payload = {
            'max length': create_simple_data(),
            'short strings': {
                'first_name': cls.get_random_str(10),
                'last_name': cls.get_random_str(10),
                cls.field_lookup: cls.get_random_str(2),
                'e_mail': cls.get_random_str(10) + '@ab.ba',
                'degree': Degrees.objects.create(name=cls.get_random_str(15)).name,
                'position': Positions.objects.create(name=cls.get_random_str(15)).name,
                'supervisor': None,
            },
            'all fields': {
                **create_simple_data(),
                'supervisor': Employees.objects.first().abbreviation,
                'year_of_studies': random.randint(1, 100),
                'is_procedure_for_a_doctoral_degree_approved': random.choices([True, False])[0],
                'has_scholarship': random.choices([True, False])[0],
            }
        }
        cls.partial_data = {
            'max length first_name': {'first_name': cls.get_random_field_str(cls.model, 'first_name')}
        }

        cls.invalid_data_payload = {
            'first_name empty': {**create_simple_data(), 'first_name': ''}
        }
        cls.invalid_partial_data = {
            'first_name empty': {'first_name': ''}
        }
