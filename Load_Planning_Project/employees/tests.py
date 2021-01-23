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

        cls.get_random_str = lambda k: ''.join(random.choices(string.ascii_letters + string.punctuation + ' _', k=k))
        cls.get_random_field_str = lambda field_name: ''.join(random.choices(
            string.ascii_letters + string.punctuation + ' _',
            k=getattr(cls.model._meta.get_field(field_name), 'max_length')))

        cls.obj_data = {cls.field_lookup: cls.get_random_field_str(cls.field_lookup)}
        cls.obj = cls.model.objects.create(**cls.obj_data)
        for i in range(3):
            cls.model.objects.create(name=cls.get_random_field_str(cls.field_lookup))

        cls.data_payload = {
            'max length': {'name': cls.get_random_field_str(cls.field_lookup)},
            'short': {'name': cls.get_random_str(k=1)},
        }
        cls.partial_data = cls.data_payload

        cls.invalid_data_payload = {
            'over max length': {'name': cls.get_random_field_str(cls.field_lookup) + 'x'},
            'empty string': {'name': ''},
        }
        cls.invalid_partial_data = cls.invalid_data_payload

    def get_obj(self, data):
        try:
            return self.model.objects.get(**{self.field_lookup: data[self.field_lookup]})
        except ObjectDoesNotExist:
            return None

    def get_kwargs(self, obj=None, valid=True):
        obj = obj if obj else self.obj
        return {self.lookup: getattr(obj, self.lookup)} if valid else {self.lookup: '100000'}

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
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"{key}: {response.data}")

    def test_get_obj_data(self, key=None):
        response = self.client.get(reverse(self.basename + '-detail', kwargs=self.get_kwargs()))
        self.assertJSONEqual(
            json.dumps(response.data), self.serializer(instance=self.obj, context=self.context).data,
            f"{key}: {response.data}")

    def test_post_data_payload_raw(self):
        for key, data in self.data_payload.items():
            response = self.client.post(reverse(self.basename + '-list'), data=data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED, f"{key}: {response.data}")
            # check if created properly
            obj = self.get_obj(data)
            self.assertIsNotNone(obj, key)
            self.test_get_obj_code(obj=obj, key=key)
            self.assertJSONEqual(
                json.dumps(response.data), self.serializer(instance=obj, context=self.context).data, key)

    def test_post_data_payload_json(self):
        for key, data in self.data_payload.items():
            response = self.client.post(
                reverse(self.basename + '-list'), data=json.dumps(data), content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED, f"{key}: {response.data}")
            # check if created properly
            obj = self.get_obj(data)
            self.assertIsNotNone(obj, key)
            self.test_get_obj_code(obj=obj, key=key)
            self.assertJSONEqual(
                json.dumps(response.data), self.serializer(instance=obj, context=self.context).data, key)

    def test_put_data_payload_raw(self):
        for key, data in self.data_payload.items():
            response = self.client.put(reverse(self.basename + '-detail', kwargs=self.get_kwargs()), data=data)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"{key}: {response.data}")
            # check if updated properly
            obj = self.get_obj(data)
            self.assertIsNotNone(obj, key)
            self.assertEqual(obj.pk, self.obj.pk, key)
            self.test_get_obj_code(obj=obj, key=key)
            self.assertJSONEqual(
                json.dumps(response.data), self.serializer(instance=obj, context=self.context).data, key)

    def test_put_data_payload_json(self):
        for key, data in self.data_payload.items():
            response = self.client.put(
                reverse(self.basename + '-detail', kwargs=self.get_kwargs()), data=json.dumps(data),
                content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"{key}: {response.data}")
            # check if updated properly
            obj = self.get_obj(data)
            self.assertIsNotNone(obj, key)
            self.assertEqual(obj.pk, self.obj.pk, key)
            self.test_get_obj_code(obj=obj, key=key)
            self.assertJSONEqual(
                json.dumps(response.data), self.serializer(instance=obj, context=self.context).data, key)

    def test_patch_data_payload_raw(self):
        for key, data in self.partial_data.items():
            response = self.client.patch(reverse(self.basename + '-detail', kwargs=self.get_kwargs()), data=data)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"{key}: {response.data}")
            # check if updated properly
            obj = self.get_obj(data)
            self.assertIsNotNone(obj, key)
            self.assertEqual(obj.pk, self.obj.pk, key)
            self.test_get_obj_code(obj=obj, key=key)
            self.assertJSONEqual(
                json.dumps(response.data), self.serializer(instance=obj, context=self.context).data, key)

    def test_patch_data_payload_json(self):
        for key, data in self.partial_data.items():
            response = self.client.patch(
                reverse(self.basename + '-detail', kwargs=self.get_kwargs()), data=json.dumps(data),
                content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"{key}: {response.data}")
            # check if updated properly
            obj = self.get_obj(data)
            self.assertIsNotNone(obj, key)
            self.assertEqual(obj.pk, self.obj.pk, key)
            self.test_get_obj_code(obj=obj, key=key)
            self.assertJSONEqual(
                json.dumps(response.data), self.serializer(instance=obj, context=self.context).data, key)

    def test_del_data(self, allowed=True):
        allowed = False if self.delete_forbidden else allowed
        response = self.client.delete(reverse(self.basename + '-detail', kwargs=self.get_kwargs()))
        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT if allowed else status.HTTP_405_METHOD_NOT_ALLOWED,
            response.data)
        # check if record has/hasn't been deleted
        if allowed:
            self.test_get_invalid(deleted_record=True)
        else:
            self.test_get_obj_code()

    # INVALID DATA TESTS

    def test_get_invalid(self, deleted_record=False):
        response = self.client.get(reverse(self.basename + '-detail', kwargs=self.get_kwargs(valid=deleted_record)))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.data)

    def test_post_invalid_data_payload_raw(self):
        number_of_records = len(self.model.objects.all())
        for key, data in self.invalid_data_payload.items():
            response = self.client.post(reverse(self.basename + '-list'), data=data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, f"{key}: {response.data}")
            # check if not created
            obj = self.get_obj(data)
            self.assertIsNone(obj, key)
            self.assertEqual(number_of_records, len(self.model.objects.all()))

    def test_post_invalid_data_payload_json(self):
        number_of_records = len(self.model.objects.all())
        for key, data in self.invalid_data_payload.items():
            response = self.client.post(
                reverse(self.basename + '-list'), data=json.dumps(data), content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, f"{key}: {response.data}")
            # check if not created
            obj = self.get_obj(data)
            self.assertIsNone(obj, key)
            self.assertEqual(number_of_records, len(self.model.objects.all()))

    def test_put_invalid_data_payload_raw(self):
        for key, data in self.invalid_data_payload.items():
            response = self.client.put(reverse(self.basename + '-detail', kwargs=self.get_kwargs()), data=data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, f"{key}: {response.data}")
            # check if not updated
            obj = self.get_obj(data)
            self.assertIsNone(obj, key)
            self.test_get_obj_code(key=key)
            self.test_get_obj_data(key=key)

    def test_put_invalid_data_payload_json(self):
        for key, data in self.invalid_data_payload.items():
            response = self.client.put(
                reverse(self.basename + '-detail', kwargs=self.get_kwargs()), data=json.dumps(data),
                content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, f"{key}: {response.data}")
            # check if not updated
            obj = self.get_obj(data)
            self.assertIsNone(obj, key)
            self.test_get_obj_code(key=key)
            self.test_get_obj_data(key=key)

    def test_patch_invalid_data_payload_raw(self):
        for key, data in self.invalid_partial_data.items():
            response = self.client.patch(reverse(self.basename + '-detail', kwargs=self.get_kwargs()), data=data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, f"{key}: {response.data}")
            # check if not updated
            obj = self.get_obj(data)
            self.assertIsNone(obj, key)
            self.test_get_obj_code(key=key)
            self.test_get_obj_data(key=key)

    def test_patch_invalid_data_payload_json(self):
        for key, data in self.invalid_partial_data.items():
            response = self.client.patch(
                reverse(self.basename + '-detail', kwargs=self.get_kwargs()), data=json.dumps(data),
                content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, f"{key}: {response.data}")
            # check if not updated
            obj = self.get_obj(data)
            self.assertIsNone(obj, key)
            self.test_get_obj_code(key=key)
            self.test_get_obj_data(key=key)

    def test_del_invalid_data(self, allowed=True):
        allowed = False if self.delete_forbidden else allowed
        response = self.client.delete(reverse(self.basename + '-detail', kwargs=self.get_kwargs(valid=False)))
        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND if allowed else status.HTTP_405_METHOD_NOT_ALLOWED,
            response.data)


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

        cls.get_random_str = lambda k: ''.join(random.choices(string.ascii_letters + string.punctuation + ' _', k=k))
        cls.get_random_field_str = lambda field_name: ''.join(random.choices(
            string.ascii_letters + string.punctuation + ' _',
            k=getattr(cls.model._meta.get_field(field_name), 'max_length')))

        cls.obj_data = {cls.field_lookup: cls.get_random_field_str(cls.field_lookup)}
        cls.obj = cls.model.objects.create(**cls.obj_data)
        for i in range(3):
            cls.model.objects.create(name=cls.get_random_field_str(cls.field_lookup))

        cls.data_payload = {
            'max length': {'name': cls.get_random_field_str(cls.field_lookup)},
            'short': {'name': cls.get_random_str(k=1)},
        }
        cls.partial_data = cls.data_payload

        cls.invalid_data_payload = {
            'over max length': {'name': cls.get_random_field_str(cls.field_lookup) + 'x'},
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

        cls.get_random_str = lambda k: ''.join(random.choices(string.ascii_letters + string.punctuation + ' _', k=k))
        cls.get_random_field_str = lambda field_name: ''.join(random.choices(
            string.ascii_letters + string.punctuation + ' _',
            k=getattr(cls.model._meta.get_field(field_name), 'max_length')))
        cls.get_random_slug = lambda field_name: ''.join(random.choices(
            string.ascii_letters + '-_', k=getattr(cls.model._meta.get_field(field_name), 'max_length')))

        cls.obj_data = {
            'first_name': cls.get_random_field_str('first_name'),
            'last_name': cls.get_random_field_str('last_name'),
            cls.field_lookup: cls.get_random_slug(cls.field_lookup),
            'e_mail': cls.get_random_slug('e_mail')[:-6] + '@ab.ba',
            'degree': Degrees.objects.create(name=cls.get_random_str(k=15)),
            'position': Positions.objects.create(name=cls.get_random_str(k=15))
        }
        cls.obj = cls.model.objects.create(**cls.obj_data)
        for i in range(0):
            cls.model.objects.create(**{
                'first_name': cls.get_random_field_str('first_name'),
                'last_name': cls.get_random_field_str('last_name'),
                cls.field_lookup: cls.get_random_slug(cls.field_lookup),
                'e_mail': cls.get_random_slug('e_mail')[:-6] + '@ab.ba',
                'degree': Degrees.objects.create(name=cls.get_random_str(k=15)),
                'position': Positions.objects.create(name=cls.get_random_str(k=15))
            })

        cls.basic_data = {
            'first_name': cls.get_random_field_str('first_name'),
            'last_name': cls.get_random_field_str('last_name'),
            cls.field_lookup: cls.get_random_slug(cls.field_lookup),
            'e_mail': cls.get_random_slug('e_mail')[:-6] + '@ab.ba',
            'degree': Degrees.objects.create(name=cls.get_random_str(k=15)).name,
            'position': Positions.objects.create(name=cls.get_random_str(k=15)).name,
            'supervisor': Employees.objects.last().abbreviation,
        }
        cls.data_payload = {
            'max length': cls.basic_data,
            'short': {
                'first_name': cls.get_random_str(k=1),
                'last_name': cls.get_random_str(k=1),
                cls.field_lookup: cls.get_random_str(k=1),
                'e_mail': cls.get_random_str(k=1),
                'degree': Degrees.objects.create(name=cls.get_random_str(k=15)).name,
                'position': Positions.objects.create(name=cls.get_random_str(k=15)).name,
                'supervisor': Employees.objects.last().abbreviation,
            },
            'complete': {
                'first_name': cls.get_random_field_str('first_name'),
                'last_name': cls.get_random_field_str('last_name'),
                cls.field_lookup: cls.get_random_slug(cls.field_lookup),
                'e_mail': cls.get_random_slug('e_mail')[:-6] + '@ab.ba',
                'degree': Degrees.objects.create(name=cls.get_random_str(k=15)).name,
                'position': Positions.objects.create(name=cls.get_random_str(k=15)).name,
                'supervisor': Employees.objects.first().abbreviation,
            }
        }
        cls.partial_data = {

        }

        cls.invalid_data_payload = {

        }
        cls.invalid_partial_data = cls.invalid_data_payload
