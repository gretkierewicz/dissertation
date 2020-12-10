import json

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory

from .models import Degrees
from .serializers import DegreeSerializer

client = APIClient()
factory = APIRequestFactory()


class DegreeViewSetTest(TestCase):
    def setUp(self):
        for i in range(3):
            Degrees.objects.create(name='degree_{}'.format(i))
        self.degree = Degrees.objects.create(name='test')
        self.name_max_len = 45
        self.valid_data = {'name': self.name_max_len * 'x'}

    def test_get_list(self):
        # try to read all records
        response = client.get(reverse('degrees-list'))
        degrees = Degrees.objects.all()
        serializer = DegreeSerializer(degrees, context={'request': factory.get('/')}, many=True)
        self.assertEqual(response.data, serializer.data, 'View response differs from serialized data')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_valid_data(self):
        # try to read one valid record
        response = client.get(reverse('degrees-detail', kwargs={'pk': self.degree.pk}))
        test_degree = Degrees.objects.get(pk=self.degree.pk)
        serializer = DegreeSerializer(test_degree, context={'request': factory.get('/')})
        self.assertEqual(serializer.data, {
            'url': factory.get(reverse('degrees-detail', kwargs={'pk': self.degree.pk})).build_absolute_uri(),
            'name': test_degree.name
        }, 'Serialization failed')
        self.assertEqual(response.data, serializer.data, 'View response differs from serialized data')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_invalid_data(self):
        # try to read not existing record
        response = client.get(reverse('degrees-detail', kwargs={'pk': 100}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_valid_data(self):
        # try to create one record
        response = client.post(reverse('degrees-list'), json.dumps(self.valid_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_invalid_data(self):
        # try to create record with invalid data
        response = client.post(
            reverse('degrees-list'),
            json.dumps({'name': ''}),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check if ErrorDetail's code is returned properly
        self.assertEqual(response.data['name'][0].code, 'blank')
        response = client.post(
            reverse('degrees-list'),
            json.dumps({'name': self.name_max_len * 'x' + 'x'}),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check if ErrorDetail's code is returned properly
        self.assertEqual(response.data['name'][0].code, 'max_length')

    def test_put_valid_data(self):
        # try to update record with valid data
        response = client.put(
            reverse('degrees-detail', kwargs={'pk': self.degree.pk}),
            json.dumps(self.valid_data),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_invalid_data(self):
        # try to update record with invalid data
        response = client.put(
            reverse('degrees-detail', kwargs={'pk': self.degree.pk}),
            json.dumps({'name': ''}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check if ErrorDetail's code is returned properly
        self.assertEqual(response.data['name'][0].code, 'blank')
        response = client.put(
            reverse('degrees-detail', kwargs={'pk': self.degree.pk}),
            json.dumps({'name': self.name_max_len * 'x' + 'x'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check if ErrorDetail's code is returned properly
        self.assertEqual(response.data['name'][0].code, 'max_length')

    def test_delete_valid(self):
        # try to delete record
        response = client.delete(reverse('degrees-detail', kwargs={'pk': self.degree.pk}))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
