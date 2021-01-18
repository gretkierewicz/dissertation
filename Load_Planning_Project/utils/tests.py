import json

from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory

from employees.models import Degrees, Positions, Employees

client = APIClient()
factory = APIRequestFactory()


def basic_degree(name='basic_degree'):
    try:
        return Degrees.objects.get(name=name)
    except ObjectDoesNotExist:
        return Degrees.objects.create(name=name)


def basic_position(name='basic_position'):
    try:
        return Positions.objects.get(name=name)
    except ObjectDoesNotExist:
        return Positions.objects.create(name=name)


def basic_supervisor(name='supervisor', abbreviation='SUPER'):
    try:
        return Employees.objects.get(abbreviation=abbreviation)
    except ObjectDoesNotExist:
        return Employees.objects.create(
            first_name=name + '_first_name',
            last_name=name + '_last_name',
            abbreviation=abbreviation,
            e_mail=name + '@basic.basic',
            degree=basic_degree(),
            position=basic_position())


def basic_employee(name='employee', abbreviation='BASIC'):
    try:
        return Employees.objects.get(abbreviation=abbreviation)
    except ObjectDoesNotExist:
        return Employees.objects.create(
            first_name=name + '_first_name',
            last_name=name + '_last_name',
            abbreviation=abbreviation,
            e_mail=name + '@basic.basic',
            degree=basic_degree(),
            position=basic_position(),
            supervisor=basic_supervisor())


class BasicMethodsTests:
    def setUp(self):
        self.basename = None
        self.model = None
        self.serializer = None
        self.basic_element = None

        self.valid_lookup_kwargs = {}
        self.valid_post_data = {}
        self.valid_put_data = self.valid_post_data
        self.valid_patch_data = self.valid_put_data

        self.invalid_lookup_kwargs = {}
        self.invalid_post_data = {}
        self.invalid_put_data = self.invalid_post_data
        self.invalid_patch_data = self.invalid_put_data

    def test_get_list(self):
        self.method_simple_test(function=client.get, url_suffix='list', status_code=status.HTTP_200_OK)

    def test_get_valid_data(self):
        self.method_simple_test(function=client.get, url_suffix='detail', url_kwargs=self.valid_lookup_kwargs,
                                status_code=status.HTTP_200_OK)

    def test_get_invalid_data(self):
        self.method_simple_test(function=client.get, url_suffix='detail', url_kwargs=self.invalid_lookup_kwargs,
                                status_code=status.HTTP_404_NOT_FOUND)

    def test_post_valid_data(self):
        self.method_simple_test(function=client.post, url_suffix='list', url_kwargs={},
                                json_data=self.valid_post_data, status_code=status.HTTP_201_CREATED)

    def test_post_invalid_data(self):
        self.method_simple_test(function=client.post, url_suffix='list', url_kwargs={},
                                json_data=self.invalid_post_data, status_code=status.HTTP_400_BAD_REQUEST)

    def test_delete_valid_data(self):
        self.method_simple_test(function=client.delete, url_suffix='detail', url_kwargs=self.valid_lookup_kwargs,
                                status_code=status.HTTP_200_OK)

    def test_delete_invalid_data(self):
        self.method_simple_test(function=client.delete, url_suffix='detail', url_kwargs=self.invalid_lookup_kwargs,
                                status_code=status.HTTP_404_NOT_FOUND)

    def test_put_valid_data(self):
        self.method_simple_test(function=client.put, url_suffix='detail', url_kwargs=self.valid_lookup_kwargs,
                                json_data=self.valid_put_data, status_code=status.HTTP_200_OK)

    def test_put_invalid_data(self):
        self.method_simple_test(function=client.put, url_suffix='detail', url_kwargs=self.valid_lookup_kwargs,
                                json_data=self.invalid_put_data, status_code=status.HTTP_400_BAD_REQUEST)

    def test_patch_valid_data(self):
        self.method_simple_test(function=client.patch, url_suffix='detail', url_kwargs=self.valid_lookup_kwargs,
                                json_data=self.valid_patch_data, status_code=status.HTTP_200_OK)

    def test_patch_invalid_data(self):
        self.method_simple_test(function=client.patch, url_suffix='detail', url_kwargs=self.valid_lookup_kwargs,
                                json_data=self.invalid_patch_data, status_code=status.HTTP_400_BAD_REQUEST)

    def method_simple_test(self, function, url_suffix, status_code, url_kwargs=None, json_data=None):
        if json_data:
            for key, data in json_data.items():
                self.assertEqual(function(reverse(self.basename+'-'+url_suffix, kwargs=url_kwargs), json.dumps(data),
                                          content_type='application/json').status_code, status_code, key)
        elif url_kwargs:
            self.assertEqual(function(reverse(self.basename+'-'+url_suffix, kwargs=url_kwargs),
                                      content_type='application/json').status_code, status_code)
        else:
            self.assertEqual(function(reverse(self.basename+'-'+url_suffix),
                                      content_type='application/json').status_code, status_code)
