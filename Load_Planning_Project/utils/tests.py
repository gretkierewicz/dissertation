import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

client = APIClient()


class StatusCodeTests:
    def setUp(self):
        self.basename = None
        self.model = None
        self.serializer = None
        self.basic_element = None

        self.valid_list_kwargs = {}
        self.valid_detail_kwargs = {}
        self.valid_post_data = {}
        self.valid_put_data = self.valid_post_data
        self.valid_patch_data = self.valid_put_data

        self.invalid_detail_kwargs = {}
        self.invalid_post_data = {}
        self.invalid_put_data = self.invalid_post_data
        self.invalid_patch_data = self.invalid_put_data

    def test_get_list(self):
        self.method_simple_test(function=client.get, url_suffix='list', url_kwargs=self.valid_list_kwargs,
                                status_code=status.HTTP_200_OK)

    def test_get_valid_data(self):
        self.method_simple_test(function=client.get, url_suffix='detail', url_kwargs=self.valid_detail_kwargs,
                                status_code=status.HTTP_200_OK)

    def test_get_invalid_data(self):
        self.method_simple_test(function=client.get, url_suffix='detail', url_kwargs=self.invalid_detail_kwargs,
                                status_code=status.HTTP_404_NOT_FOUND)

    def test_post_valid_data(self):
        self.method_simple_test(function=client.post, url_suffix='list', url_kwargs=self.valid_list_kwargs,
                                json_data=self.valid_post_data, status_code=status.HTTP_201_CREATED)

    def test_post_invalid_data(self):
        self.method_simple_test(function=client.post, url_suffix='list', url_kwargs=self.valid_list_kwargs,
                                json_data=self.invalid_post_data, status_code=status.HTTP_400_BAD_REQUEST)

    def test_delete_valid_data(self):
        self.method_simple_test(function=client.delete, url_suffix='detail', url_kwargs=self.valid_detail_kwargs,
                                status_code=status.HTTP_204_NO_CONTENT)

    def test_delete_invalid_data(self):
        self.method_simple_test(function=client.delete, url_suffix='detail', url_kwargs=self.invalid_detail_kwargs,
                                status_code=status.HTTP_404_NOT_FOUND)

    def test_put_valid_data(self):
        self.method_simple_test(function=client.put, url_suffix='detail', url_kwargs=self.valid_detail_kwargs,
                                json_data=self.valid_put_data, status_code=status.HTTP_200_OK)

    def test_put_invalid_data(self):
        self.method_simple_test(function=client.put, url_suffix='detail', url_kwargs=self.valid_detail_kwargs,
                                json_data=self.invalid_put_data, status_code=status.HTTP_400_BAD_REQUEST)

    def test_patch_valid_data(self):
        self.method_simple_test(function=client.patch, url_suffix='detail', url_kwargs=self.valid_detail_kwargs,
                                json_data=self.valid_patch_data, status_code=status.HTTP_200_OK)

    def test_patch_invalid_data(self):
        self.method_simple_test(function=client.patch, url_suffix='detail', url_kwargs=self.valid_detail_kwargs,
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
