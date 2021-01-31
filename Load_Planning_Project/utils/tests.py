import json
import unittest

from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


class BasicAPITests:
    @classmethod
    def setUpTestData(cls):
        """
        Fill all this data for tests to work properly
        """
        cls.client = None
        cls.factory = None

        cls.model = None
        cls.serializer = None
        cls.list_serializer = None
        cls.basename = None
        cls.list_suffix = 'list'
        cls.detail_suffix = 'detail'
        cls.context = None
        cls.lookup = None
        cls.field_lookup = None
        cls.delete_forbidden = False

        cls.obj = None

        cls.valid_post_data_payload = None
        cls.valid_put_data_payload = cls.valid_post_data_payload
        cls.valid_partial_data = cls.valid_post_data_payload

        cls.invalid_post_data_payload = None
        cls.invalid_put_data_payload = cls.invalid_post_data_payload
        cls.invalid_partial_data = cls.invalid_post_data_payload

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
        if self.client and self.basename and self.list_suffix:
            response = self.client.get(reverse(self.basename + '-' + self.list_suffix))
            self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        else:
            APITestCase.skipTest(self, 'Lack of data')

    def test_get_list_data(self):
        if self.client and self.basename and self.model and self.list_serializer and self.list_suffix:
            response = self.client.get(reverse(self.basename + '-' + self.list_suffix))
            self.assertJSONEqual(
                json.dumps(response.data),
                self.list_serializer(instance=self.model.objects.all(), many=True, context=self.context).data,
                response.data)
        else:
            APITestCase.skipTest(self, 'Lack of data')

    def test_get_obj_code(self, obj=None, msg=None):
        if self.client and self.basename and self.detail_suffix:
            response = self.client.get(reverse(self.basename + '-' + self.detail_suffix, kwargs=self.get_kwargs(obj)))
            self.assertEqual(response.status_code, status.HTTP_200_OK, (f"{msg}: " if msg else "") + f"{response.data}")
        else:
            APITestCase.skipTest(self, 'Lack of data')

    def test_get_obj_data(self, obj=None, msg=None):
        if self.client and self.basename and self.serializer and self.detail_suffix:
            response = self.client.get(reverse(self.basename + '-' + self.detail_suffix, kwargs=self.get_kwargs(obj)))
            self.assertJSONEqual(
                json.dumps(response.data), self.serializer(instance=(obj or self.obj), context=self.context).data,
                (f"{msg}: " if msg else "") + f"{response.data}")
        else:
            APITestCase.skipTest(self, 'Lack of data')

    def test_post_data_payload_raw(self, payload_data=None):
        if self.client and self.basename and self.list_suffix:
            for msg, data in (payload_data or self.valid_post_data_payload).items():
                with APITestCase.subTest(self, msg):
                    response = self.client.post(reverse(self.basename + '-' + self.list_suffix), data=data)
                    self.assertEqual(response.status_code, status.HTTP_201_CREATED, f"{response.data}")
                    # try to get created model instance
                    obj = self.get_obj(data)
                    self.assertIsNotNone(obj)
                    # check response code with get method
                    self.test_get_obj_code(obj=obj, msg=msg)
                    # check data integrity of data sent and serialized instance
                    if self.serializer:
                        self.assertJSONEqual(
                            json.dumps(response.data), self.serializer(instance=obj, context=self.context).data)
        else:
            APITestCase.skipTest(self, 'Lack of data')

    def test_post_data_payload_json(self, payload_data=None):
        if self.client and self.basename and self.list_suffix:
            for msg, data in (payload_data or self.valid_post_data_payload).items():
                with APITestCase.subTest(self, msg):
                    response = self.client.post(
                        reverse(self.basename + '-' + self.list_suffix),
                        data=json.dumps(data),
                        content_type='application/json')
                    self.assertEqual(response.status_code, status.HTTP_201_CREATED, f"{response.data}")
                    # try to get created model instance
                    obj = self.get_obj(data)
                    self.assertIsNotNone(obj)
                    # check response code with get method
                    self.test_get_obj_code(obj=obj, msg=msg)
                    # check data integrity of data sent and serialized instance
                    if self.serializer:
                        self.assertJSONEqual(
                            json.dumps(response.data), self.serializer(instance=obj, context=self.context).data)
        else:
            APITestCase.skipTest(self, 'Lack of data')

    def test_put_data_payload_raw(self, base_obj=None, payload_data=None):
        if self.client and self.basename and self.detail_suffix:
            obj = base_obj
            for msg, data in (payload_data or self.valid_post_data_payload).items():
                with APITestCase.subTest(self, msg):
                    response = self.client.put(
                        reverse(self.basename + '-' + self.detail_suffix, kwargs=self.get_kwargs(obj)), data=data)
                    self.assertEqual(response.status_code, status.HTTP_200_OK, f"{response.data}")
                    # try to get updated model instance
                    obj = self.get_obj(data)
                    self.assertIsNotNone(obj)
                    self.assertEqual(obj.pk, self.obj.pk)
                    # check response code with get method
                    self.test_get_obj_code(obj=obj, msg=msg)
                    # check data integrity of data sent and serialized instance
                    if self.serializer:
                        self.assertJSONEqual(
                            json.dumps(response.data), self.serializer(instance=obj, context=self.context).data)
        else:
            APITestCase.skipTest(self, 'Lack of data')

    def test_put_data_payload_json(self, base_obj=None, payload_data=None):
        if self.client and self.basename and self.detail_suffix:
            obj = base_obj
            for msg, data in (payload_data or self.valid_post_data_payload).items():
                with APITestCase.subTest(self, msg):
                    response = self.client.put(
                        reverse(self.basename + '-' + self.detail_suffix, kwargs=self.get_kwargs(obj)),
                        data=json.dumps(data),
                        content_type='application/json')
                    self.assertEqual(response.status_code, status.HTTP_200_OK, f"{response.data}")
                    # try to get updated model instance
                    obj = self.get_obj(data)
                    self.assertIsNotNone(obj)
                    self.assertEqual(obj.pk, self.obj.pk)
                    # check response code with get method
                    self.test_get_obj_code(obj=obj, msg=msg)
                    # check data integrity of data sent and serialized instance
                    if self.serializer:
                        self.assertJSONEqual(
                            json.dumps(response.data), self.serializer(instance=obj, context=self.context).data)
        else:
            APITestCase.skipTest(self, 'Lack of data')

    def test_patch_data_payload_raw(self, base_obj=None, payload_data=None):
        if self.client and self.basename and self.detail_suffix:
            obj = base_obj
            for msg, data in (payload_data or self.valid_partial_data).items():
                with APITestCase.subTest(self, msg):
                    response = self.client.patch(
                        reverse(self.basename + '-' + self.detail_suffix, kwargs=self.get_kwargs(obj)), data=data)
                    self.assertEqual(response.status_code, status.HTTP_200_OK, f"{response.data}")
                    # try to get updated model instance
                    obj = self.get_obj_by_pk(self.obj.pk)
                    self.assertIsNotNone(obj)
                    # check response code with get method
                    self.test_get_obj_code(obj=obj, msg=msg)
                    # check data integrity of data sent and serialized instance
                    if self.serializer:
                        self.assertJSONEqual(
                            json.dumps(response.data), self.serializer(instance=obj, context=self.context).data)
        else:
            APITestCase.skipTest(self, 'Lack of data')

    def test_patch_data_payload_json(self, base_obj=None, payload_data=None):
        if self.client and self.basename and self.detail_suffix:
            obj = base_obj
            for msg, data in (payload_data or self.valid_partial_data).items():
                with APITestCase.subTest(self, msg):
                    response = self.client.patch(
                        reverse(self.basename + '-' + self.detail_suffix, kwargs=self.get_kwargs(obj)),
                        data=json.dumps(data),
                        content_type='application/json')
                    self.assertEqual(response.status_code, status.HTTP_200_OK, f"{response.data}")
                    # try to get updated model instance
                    obj = self.get_obj_by_pk(self.obj.pk)
                    self.assertIsNotNone(obj)
                    # check response code with get method
                    self.test_get_obj_code(obj=obj, msg=msg)
                    # check data integrity of data sent and serialized instance
                    if self.serializer:
                        self.assertJSONEqual(
                            json.dumps(response.data), self.serializer(instance=obj, context=self.context).data)
        else:
            APITestCase.skipTest(self, 'Lack of data')

    def test_del_data(self, obj=None):
        if self.client and self.basename and self.detail_suffix:
            response = self.client.delete(
                reverse(self.basename + '-' + self.detail_suffix, kwargs=self.get_kwargs(obj)))
            self.assertEqual(
                response.status_code,
                status.HTTP_405_METHOD_NOT_ALLOWED if self.delete_forbidden else status.HTTP_204_NO_CONTENT,
                response.data)
            # check if record has/hasn't been deleted
            if self.delete_forbidden:
                self.test_get_obj_code(obj)
            else:
                self.test_get_invalid(deleted_record=True)
        else:
            APITestCase.skipTest(self, 'Lack of data')

    # INVALID DATA TESTS

    def test_get_invalid(self, deleted_record=False):
        if self.client and self.basename and self.detail_suffix:
            response = self.client.get(
                reverse(self.basename + '-' + self.detail_suffix, kwargs=self.get_kwargs(valid=deleted_record)))
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.data)
        else:
            APITestCase.skipTest(self, 'Lack of data')

    def test_post_invalid_data_payload_raw(self, payload_data=None):
        if self.client and self.basename and self.list_suffix:
            records = [_.pk for _ in self.model.objects.all()]
            for msg, data in (payload_data or self.invalid_post_data_payload).items():
                with APITestCase.subTest(self, msg):
                    response = self.client.post(reverse(self.basename + '-' + self.list_suffix), data=data)
                    self.assertEqual(
                        response.status_code, status.HTTP_400_BAD_REQUEST, f"{response.data}")
                    # double check records' pks
                    self.assertEqual(records, [_.pk for _ in self.model.objects.all()])
        else:
            APITestCase.skipTest(self, 'Lack of data')

    def test_post_invalid_data_payload_json(self, payload_data=None):
        if self.client and self.basename and self.list_suffix:
            records = [_.pk for _ in self.model.objects.all()]
            for msg, data in (payload_data or self.invalid_post_data_payload).items():
                with APITestCase.subTest(self, msg):
                    response = self.client.post(
                        reverse(self.basename + '-' + self.list_suffix),
                        data=json.dumps(data),
                        content_type='application/json')
                    self.assertEqual(
                        response.status_code, status.HTTP_400_BAD_REQUEST, f"{response.data}")
                    # double check records' pks
                    self.assertEqual(records, [_.pk for _ in self.model.objects.all()])
        else:
            APITestCase.skipTest(self, 'Lack of data')

    def test_put_invalid_data_payload_raw(self, base_obj=None, payload_data=None):
        if self.client and self.basename and self.detail_suffix:
            for msg, data in (payload_data or self.invalid_put_data_payload).items():
                with APITestCase.subTest(self, msg):
                    response = self.client.put(
                        reverse(self.basename + '-' + self.detail_suffix, kwargs=self.get_kwargs(base_obj)), data=data)
                    self.assertEqual(
                        response.status_code, status.HTTP_400_BAD_REQUEST, f"{response.data}")
                    # check if self.obj was not changed
                    self.test_get_obj_data(obj=base_obj, msg=msg)
        else:
            APITestCase.skipTest(self, 'Lack of data')

    def test_put_invalid_data_payload_json(self, base_obj=None, payload_data=None):
        if self.client and self.basename and self.detail_suffix:
            for msg, data in (payload_data or self.invalid_put_data_payload).items():
                with APITestCase.subTest(self, msg):
                    response = self.client.put(
                        reverse(self.basename + '-' + self.detail_suffix, kwargs=self.get_kwargs(base_obj)),
                        data=json.dumps(data),
                        content_type='application/json')
                    self.assertEqual(
                        response.status_code, status.HTTP_400_BAD_REQUEST, f"{response.data}")
                    # check if self.obj was not changed
                    self.test_get_obj_data(obj=base_obj, msg=msg)
        else:
            APITestCase.skipTest(self, 'Lack of data')

    def test_patch_invalid_data_payload_raw(self, base_obj=None, payload_data=None):
        if self.client and self.basename and self.detail_suffix:
            for msg, data in (payload_data or self.invalid_partial_data).items():
                with APITestCase.subTest(self, msg):
                    response = self.client.patch(
                        reverse(self.basename + '-' + self.detail_suffix, kwargs=self.get_kwargs(base_obj)), data=data)
                    self.assertEqual(
                        response.status_code, status.HTTP_400_BAD_REQUEST, f"{response.data}")
                    # check if self.obj was not changed
                    self.test_get_obj_data(obj=base_obj, msg=msg)
        else:
            APITestCase.skipTest(self, 'Lack of data')

    def test_patch_invalid_data_payload_json(self, base_obj=None, payload_data=None):
        if self.client and self.basename and self.detail_suffix:
            for msg, data in (payload_data or self.invalid_partial_data).items():
                with APITestCase.subTest(self, msg):
                    response = self.client.patch(
                        reverse(self.basename + '-' + self.detail_suffix, kwargs=self.get_kwargs(base_obj)),
                        data=json.dumps(data),
                        content_type='application/json')
                    self.assertEqual(
                        response.status_code, status.HTTP_400_BAD_REQUEST, f"{response.data}")
                    # check if self.obj was not changed
                    self.test_get_obj_data(obj=base_obj, msg=msg)
        else:
            APITestCase.skipTest(self, 'Lack of data')

    def test_del_invalid_data(self):
        if self.client and self.basename and self.detail_suffix:
            response = self.client.delete(
                reverse(self.basename + '-' + self.detail_suffix, kwargs=self.get_kwargs(valid=False)))
            self.assertEqual(
                response.status_code,
                status.HTTP_405_METHOD_NOT_ALLOWED if self.delete_forbidden else status.HTTP_404_NOT_FOUND,
                response.data)
        else:
            APITestCase.skipTest(self, 'Lack of data')
