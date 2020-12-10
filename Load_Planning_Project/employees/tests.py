from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory

from .models import Degrees
from .serializers import DegreeSerializer

client = APIClient()
factory = APIRequestFactory()


class GetAllDegreesTest(TestCase):
    def setUp(self):
        for i in range(5):
            Degrees.objects.create(name='degree_{}'.format(i))

    def test_get_degrees_list(self):
        response = client.get(reverse('degrees-list'))

        degrees = Degrees.objects.all()
        request = factory.get('/')
        serializer = DegreeSerializer(degrees, context={'request': request}, many=True)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
