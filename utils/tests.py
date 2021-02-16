import json
import re

from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


def get_obj_with_parent_kwargs(func):
    """
    Helper decorator for cases of OneToOne relations - getting instance from obj_parent_get_kwargs or lookup
    obj_parent_get_kwargs must provide lookups and values of main obj in dictionary form.
    If provided with data, lookup and field_lookup, it should get parent from passed URL in data.
    This solves problem of getting parent after posting data with URL that do not provide data about it.
    """
    def wrapper(self, *args, **kwargs):
        if hasattr(self, 'obj_parent_get_kwargs') and self.obj_parent_get_kwargs:
            parent_kwargs = None
            if len(args) > 0 and self.lookup:
                # if data dictionary passed
                parent_kwargs = {}
                if args[0].get(self.field_lookup):
                    for key, re_pattern in self.lookup.items():
                        answ = re.search(re_pattern, args[0].get(self.field_lookup))
                        parent_kwargs[key] = answ[key]
            try:
                return self.model.objects.get(**(parent_kwargs or self.obj_parent_get_kwargs))
            except ObjectDoesNotExist:
                return None
        return func(self, *args, **kwargs)
    return wrapper


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
        cls.list_view_name = None
        cls.detail_view_name = None
        cls.context = None
        cls.lookup = None
        cls.field_lookup = None
        cls.obj_parent_url_kwargs = None
        cls.obj_parent_get_kwargs = None
        cls.delete_forbidden = False

        cls.obj = None

        cls.valid_post_data_payload = None
        cls.valid_put_data_payload = cls.valid_post_data_payload
        cls.valid_partial_data = cls.valid_post_data_payload

        cls.invalid_post_data_payload = None
        cls.invalid_put_data_payload = cls.invalid_post_data_payload
        cls.invalid_partial_data = cls.invalid_post_data_payload

    @get_obj_with_parent_kwargs
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
        if valid:
            if hasattr(self, 'obj_parent_url_kwargs'):
                return self.obj_parent_url_kwargs
            return {self.lookup: getattr((obj or self.obj), self.lookup)}
        # if not valid:
        if hasattr(self, 'obj_parent_url_kwargs') and self.obj_parent_url_kwargs:
            return {key: '99999999' for key, _ in self.obj_parent_url_kwargs.items()}
        return {self.lookup or 'pk': '99999'}

    def test_get_list_code(self):
        if self.client and self.list_view_name:
            response = self.client.get(reverse(self.list_view_name))
            self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        else:
            APITestCase.skipTest(self, 'Lack of data')

    def test_get_list_data(self):
        if self.client and self.list_view_name and self.model and self.list_serializer:
            response = self.client.get(reverse(self.list_view_name))
            self.assertJSONEqual(
                json.dumps(response.data),
                self.list_serializer(instance=self.model.objects.all(), many=True, context=self.context).data,
                response.data)
        else:
            APITestCase.skipTest(self, 'Lack of data')

    def test_get_obj_code(self, obj=None, msg=None):
        if self.client and self.detail_view_name:
            response = self.client.get(reverse(self.detail_view_name, kwargs=self.get_kwargs(obj)))
            self.assertEqual(response.status_code, status.HTTP_200_OK, (f"{msg}: " if msg else "") + f"{response.data}")
        else:
            APITestCase.skipTest(self, 'Lack of data')

    def test_get_obj_data(self, obj=None, msg=None):
        if self.client and self.detail_view_name and self.serializer:
            response = self.client.get(reverse(self.detail_view_name, kwargs=self.get_kwargs(obj)))
            self.assertJSONEqual(
                json.dumps(response.data), self.serializer(instance=(obj or self.obj), context=self.context).data,
                (f"{msg}: " if msg else "") + f"{response.data}")
        else:
            APITestCase.skipTest(self, 'Lack of data')

    def test_post_data_payload_raw(self, payload_data=None):
        if self.client and self.list_view_name:
            for msg, data in (payload_data or self.valid_post_data_payload).items():
                with APITestCase.subTest(self, msg):
                    response = self.client.post(reverse(self.list_view_name), data=data)
                    self.assertEqual(response.status_code, status.HTTP_201_CREATED, f"{response.data}")
                    # try to get created model instance
                    obj = self.get_obj(data)
                    self.assertIsNotNone(obj)
                    # check response code with get method
                    self.test_get_obj_code(obj=obj, msg=msg)
                    # check data integrity of data sent and serialized instance
                    if self.list_serializer:
                        self.assertJSONEqual(
                            json.dumps(response.data), self.list_serializer(instance=obj, context=self.context).data)
        else:
            APITestCase.skipTest(self, 'Lack of data')

    def test_post_data_payload_json(self, payload_data=None):
        if self.client and self.list_view_name:
            for msg, data in (payload_data or self.valid_post_data_payload).items():
                with APITestCase.subTest(self, msg):
                    response = self.client.post(
                        reverse(self.list_view_name),
                        data=json.dumps(data),
                        content_type='application/json')
                    self.assertEqual(response.status_code, status.HTTP_201_CREATED, f"{response.data}")
                    # try to get created model instance
                    obj = self.get_obj(data)
                    self.assertIsNotNone(obj)
                    # check response code with get method
                    self.test_get_obj_code(obj=obj, msg=msg)
                    # check data integrity of data sent and serialized instance
                    if self.list_serializer:
                        self.assertJSONEqual(
                            json.dumps(response.data), self.list_serializer(instance=obj, context=self.context).data)
        else:
            APITestCase.skipTest(self, 'Lack of data')

    def test_put_data_payload_raw(self, base_obj=None, payload_data=None):
        if self.client and self.detail_view_name:
            obj = base_obj
            for msg, data in (payload_data or self.valid_put_data_payload).items():
                with APITestCase.subTest(self, msg):
                    response = self.client.put(
                        reverse(self.detail_view_name, kwargs=self.get_kwargs(obj)), data=data)
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
        if self.client and self.detail_view_name:
            obj = base_obj
            for msg, data in (payload_data or self.valid_put_data_payload).items():
                with APITestCase.subTest(self, msg):
                    response = self.client.put(
                        reverse(self.detail_view_name, kwargs=self.get_kwargs(obj)),
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
        if self.client and self.detail_view_name:
            obj = base_obj
            for msg, data in (payload_data or self.valid_partial_data).items():
                with APITestCase.subTest(self, msg):
                    response = self.client.patch(
                        reverse(self.detail_view_name, kwargs=self.get_kwargs(obj)), data=data)
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
        if self.client and self.detail_view_name:
            obj = base_obj
            for msg, data in (payload_data or self.valid_partial_data).items():
                with APITestCase.subTest(self, msg):
                    response = self.client.patch(
                        reverse(self.detail_view_name, kwargs=self.get_kwargs(obj)),
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
        if self.client and self.detail_view_name:
            response = self.client.delete(
                reverse(self.detail_view_name, kwargs=self.get_kwargs(obj)))
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
        if self.client and self.detail_view_name:
            response = self.client.get(
                reverse(self.detail_view_name, kwargs=self.get_kwargs(valid=deleted_record)))
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.data)
        else:
            APITestCase.skipTest(self, 'Lack of data')

    def test_post_invalid_data_payload_raw(self, payload_data=None):
        if self.client and self.list_view_name:
            records = [_.pk for _ in self.model.objects.all()]
            for msg, data in (payload_data or self.invalid_post_data_payload).items():
                with APITestCase.subTest(self, msg):
                    response = self.client.post(reverse(self.list_view_name), data=data)
                    self.assertEqual(
                        response.status_code, status.HTTP_400_BAD_REQUEST, f"{response.data}")
                    # double check records' pks
                    self.assertEqual(records, [_.pk for _ in self.model.objects.all()])
        else:
            APITestCase.skipTest(self, 'Lack of data')

    def test_post_invalid_data_payload_json(self, payload_data=None):
        if self.client and self.list_view_name:
            records = [_.pk for _ in self.model.objects.all()]
            for msg, data in (payload_data or self.invalid_post_data_payload).items():
                with APITestCase.subTest(self, msg):
                    response = self.client.post(
                        reverse(self.list_view_name),
                        data=json.dumps(data),
                        content_type='application/json')
                    self.assertEqual(
                        response.status_code, status.HTTP_400_BAD_REQUEST, f"{response.data}")
                    # double check records' pks
                    self.assertEqual(records, [_.pk for _ in self.model.objects.all()])
        else:
            APITestCase.skipTest(self, 'Lack of data')

    def test_put_invalid_data_payload_raw(self, base_obj=None, payload_data=None):
        if self.client and self.detail_view_name:
            for msg, data in (payload_data or self.invalid_put_data_payload).items():
                with APITestCase.subTest(self, msg):
                    response = self.client.put(
                        reverse(self.detail_view_name, kwargs=self.get_kwargs(base_obj)), data=data)
                    self.assertEqual(
                        response.status_code, status.HTTP_400_BAD_REQUEST, f"{response.data}")
                    # check if self.obj was not changed
                    self.test_get_obj_data(obj=base_obj, msg=msg)
        else:
            APITestCase.skipTest(self, 'Lack of data')

    def test_put_invalid_data_payload_json(self, base_obj=None, payload_data=None):
        if self.client and self.detail_view_name:
            for msg, data in (payload_data or self.invalid_put_data_payload).items():
                with APITestCase.subTest(self, msg):
                    response = self.client.put(
                        reverse(self.detail_view_name, kwargs=self.get_kwargs(base_obj)),
                        data=json.dumps(data),
                        content_type='application/json')
                    self.assertEqual(
                        response.status_code, status.HTTP_400_BAD_REQUEST, f"{response.data}")
                    # check if self.obj was not changed
                    self.test_get_obj_data(obj=base_obj, msg=msg)
        else:
            APITestCase.skipTest(self, 'Lack of data')

    def test_patch_invalid_data_payload_raw(self, base_obj=None, payload_data=None):
        if self.client and self.detail_view_name:
            for msg, data in (payload_data or self.invalid_partial_data).items():
                with APITestCase.subTest(self, msg):
                    response = self.client.patch(
                        reverse(self.detail_view_name, kwargs=self.get_kwargs(base_obj)), data=data)
                    self.assertEqual(
                        response.status_code, status.HTTP_400_BAD_REQUEST, f"{response.data}")
                    # check if self.obj was not changed
                    self.test_get_obj_data(obj=base_obj, msg=msg)
        else:
            APITestCase.skipTest(self, 'Lack of data')

    def test_patch_invalid_data_payload_json(self, base_obj=None, payload_data=None):
        if self.client and self.detail_view_name:
            for msg, data in (payload_data or self.invalid_partial_data).items():
                with APITestCase.subTest(self, msg):
                    response = self.client.patch(
                        reverse(self.detail_view_name, kwargs=self.get_kwargs(base_obj)),
                        data=json.dumps(data),
                        content_type='application/json')
                    self.assertEqual(
                        response.status_code, status.HTTP_400_BAD_REQUEST, f"{response.data}")
                    # check if self.obj was not changed
                    self.test_get_obj_data(obj=base_obj, msg=msg)
        else:
            APITestCase.skipTest(self, 'Lack of data')

    def test_del_invalid_data(self):
        if self.client and self.detail_view_name:
            response = self.client.delete(
                reverse(self.detail_view_name, kwargs=self.get_kwargs(valid=False)))
            self.assertEqual(
                response.status_code,
                status.HTTP_405_METHOD_NOT_ALLOWED if self.delete_forbidden else status.HTTP_404_NOT_FOUND,
                response.data)
        else:
            APITestCase.skipTest(self, 'Lack of data')
