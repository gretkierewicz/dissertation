import json

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory

from .models import Degrees, Positions, Employees
from .serializers import DegreeSerializer, PositionSerializer, EmployeeSerializer

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


class PositionViewSetTest(TestCase):
    def setUp(self):
        for i in range(3):
            Positions.objects.create(name='position_{}'.format(i))
        self.position = Positions.objects.create(name='test')
        self.name_max_len = 45
        self.valid_data = {'name': self.name_max_len * 'x'}

    def test_get_list(self):
        # try to read all records
        response = client.get(reverse('positions-list'))
        positions = Positions.objects.all()
        serializer = PositionSerializer(positions, context={'request': factory.get('/')}, many=True)
        self.assertEqual(response.data, serializer.data, 'View response differs from serialized data')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_valid_data(self):
        # try to read one valid record
        response = client.get(reverse('positions-detail', kwargs={'pk': self.position.pk}))
        test_position = Positions.objects.get(pk=self.position.pk)
        serializer = PositionSerializer(test_position, context={'request': factory.get('/')})
        self.assertEqual(serializer.data, {
            'url': factory.get(reverse('positions-detail', kwargs={'pk': self.position.pk})).build_absolute_uri(),
            'name': test_position.name
        }, 'Serialization failed')
        self.assertEqual(response.data, serializer.data, 'View response differs from serialized data')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_invalid_data(self):
        # try to read not existing record
        response = client.get(reverse('positions-detail', kwargs={'pk': 100}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_valid_data(self):
        # try to create one record
        response = client.post(reverse('positions-list'), json.dumps(self.valid_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_invalid_data(self):
        # try to create record with invalid data
        response = client.post(
            reverse('positions-list'),
            json.dumps({'name': ''}),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check if ErrorDetail's code is returned properly
        self.assertEqual(response.data['name'][0].code, 'blank')
        response = client.post(
            reverse('positions-list'),
            json.dumps({'name': self.name_max_len * 'x' + 'x'}),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check if ErrorDetail's code is returned properly
        self.assertEqual(response.data['name'][0].code, 'max_length')

    def test_put_valid_data(self):
        # try to update record with valid data
        response = client.put(
            reverse('positions-detail', kwargs={'pk': self.position.pk}),
            json.dumps(self.valid_data),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_invalid_data(self):
        # try to update record with invalid data
        response = client.put(
            reverse('positions-detail', kwargs={'pk': self.position.pk}),
            json.dumps({'name': ''}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check if ErrorDetail's code is returned properly
        self.assertEqual(response.data['name'][0].code, 'blank')
        response = client.put(
            reverse('positions-detail', kwargs={'pk': self.position.pk}),
            json.dumps({'name': self.name_max_len * 'x' + 'x'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check if ErrorDetail's code is returned properly
        self.assertEqual(response.data['name'][0].code, 'max_length')

    def test_delete_valid(self):
        # try to delete record
        response = client.delete(reverse('positions-detail', kwargs={'pk': self.position.pk}))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class EmployeesViewSetTest(TestCase):
    def setUp(self):
        self.degree = Degrees.objects.create(name='degree_name')
        self.position = Positions.objects.create(name='position_name')
        self.employee = None
        for i in range(3):
            self.employee = Employees.objects.create(
                first_name='first name_{}'.format(i),
                last_name='last_name_{}'.format(i),
                abbreviation='abb{}'.format(i),
                degree=self.degree,
                position=self.position,
                e_mail='x{}@x.xx'.format(i),
                supervisor=self.employee,
                year_of_studies=i,
            )
        self.first_name_max_len = 45
        self.last_name_max_len = 45
        self.abbreviation_max_len = 5
        self.e_mail_max_len = 45
        self.valid_data = {
            'first_name': self.first_name_max_len * 'x',
            'last_name': self.last_name_max_len * 'x',
            'abbreviation': self.abbreviation_max_len * 'x',
            'degree': client.get(reverse('degrees-detail', kwargs={'pk': self.degree.pk})).data.get('url'),
            'position': client.get(reverse('positions-detail', kwargs={'pk': self.position.pk})).data.get('url'),
            'e_mail': (self.e_mail_max_len - 5) * 'x' + '@x.xx',
            'supervisor': client.get(reverse('employees-detail', kwargs={'pk': self.employee.pk})).data.get('url'),
            'year_of_studies': 1,
            'is_procedure_for_a_doctoral_degree_approved': True,
            'has_scholarship': True,
        }
        self.valid_data_min = {
            'first_name': 'a',
            'last_name': 'a',
            'abbreviation': 'a',
            'degree': client.get(reverse('degrees-detail', kwargs={'pk': self.degree.pk})).data.get('url'),
            'position': client.get(reverse('positions-detail', kwargs={'pk': self.position.pk})).data.get('url'),
            'e_mail': 'a@a.aa',
            'supervisor': None,
        }

    def test_get_list(self):
        # try to read all records
        response = client.get(reverse('employees-list'))
        employees = Employees.objects.all()
        serializer = EmployeeSerializer(employees, context={'request': factory.get('/')}, many=True)
        self.assertEqual(response.data, serializer.data, 'View response differs from serialized data')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_valid_data(self):
        # try to read one valid record
        response = client.get(reverse('employees-detail', kwargs={'pk': self.employee.pk}))
        test_employee = Employees.objects.get(pk=self.employee.pk)
        serializer = EmployeeSerializer(test_employee, context={'request': factory.get('/')})
        self.assertEqual(serializer.data['url'],
                         factory.get(reverse('employees-detail', kwargs={'pk': self.employee.pk})).build_absolute_uri(),
                         "'url' field do not match!")
        self.assertEqual(serializer.data['first_name'],
                         self.employee.first_name,
                         "'first_name' field do not match!")
        self.assertEqual(serializer.data['last_name'],
                         self.employee.last_name,
                         "'last_name' field do not match!")
        self.assertEqual(serializer.data['abbreviation'],
                         self.employee.abbreviation,
                         "'abbreviation' field do not match!")
        self.assertEqual(serializer.data['degree'],
                         factory.get(reverse('degrees-detail', kwargs={'pk': self.degree.pk})).build_absolute_uri(),
                         "'degree' field do not match!")
        self.assertEqual(serializer.data['degree_repr'],
                         self.employee.degree.name,
                         "'degree_repr' field do not match!")
        self.assertEqual(serializer.data['position'],
                         factory.get(reverse('positions-detail', kwargs={'pk': self.position.pk})).build_absolute_uri(),
                         "'position' field do not match!")
        self.assertEqual(serializer.data['position_repr'],
                         self.employee.position.name,
                         "'position_repr' field do not match!")
        self.assertEqual(serializer.data['e_mail'],
                         self.employee.e_mail,
                         "'e_mail' field do not match!")
        self.assertEqual(serializer.data['supervisor'],
                         factory.get(reverse('employees-detail',
                                             kwargs={'pk': self.employee.supervisor.pk})).build_absolute_uri(),
                         "'supervisor' field do not match!")
        self.assertEqual(serializer.data['year_of_studies'],
                         self.employee.year_of_studies,
                         "'year_of_studies' field do not match!")
        self.assertEqual(serializer.data['is_procedure_for_a_doctoral_degree_approved'],
                         self.employee.is_procedure_for_a_doctoral_degree_approved,
                         "'is_procedure_for_a_doctoral_degree_approved' field do not match!")
        self.assertEqual(serializer.data['has_scholarship'],
                         self.employee.has_scholarship,
                         "'has_scholarship' field do not match!")
        self.assertEqual(response.data, serializer.data, 'View response differs from serialized data')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_invalid_data(self):
        # try to read not existing record
        response = client.get(reverse('employees-detail', kwargs={'pk': 100}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_valid_data(self):
        # try to create one record with valid data
        response = client.post(reverse('employees-list'), json.dumps(self.valid_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_valid_min_data(self):
        # try to create one record with min data
        response = client.post(reverse('employees-list'),
                               json.dumps(self.valid_data_min),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_valid_year_of_studies_min(self):
        # try to create one record with min data
        valid_data_with_year = self.valid_data

        valid_data_with_year['year_of_studies'] = 0
        response = client.post(reverse('employees-list'),
                               json.dumps(valid_data_with_year),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_valid_year_of_studies_max(self):
        # try to create one record with min data
        valid_data_with_year = self.valid_data

        valid_data_with_year['year_of_studies'] = 100
        response = client.post(reverse('employees-list'),
                               json.dumps(valid_data_with_year),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_invalid_first_name(self):
        # try to create one record with invalid data for first name
        invalid_data = self.valid_data

        invalid_data['first_name'] = None
        response = client.post(reverse('employees-list'), json.dumps(invalid_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check if ErrorDetail's code is returned properly
        self.assertEqual(response.data['first_name'][0].code, 'null')

        invalid_data['first_name'] = ''
        response = client.post(reverse('employees-list'), json.dumps(invalid_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check if ErrorDetail's code is returned properly
        self.assertEqual(response.data['first_name'][0].code, 'blank')

        invalid_data['first_name'] = self.first_name_max_len * 'x' + 'x'
        response = client.post(reverse('employees-list'), json.dumps(invalid_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check if ErrorDetail's code is returned properly
        self.assertEqual(response.data['first_name'][0].code, 'max_length')

    def test_post_invalid_last_name(self):
        # try to create one record with invalid data for last name
        invalid_data = self.valid_data

        invalid_data['last_name'] = None
        response = client.post(reverse('employees-list'), json.dumps(invalid_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check if ErrorDetail's code is returned properly
        self.assertEqual(response.data['last_name'][0].code, 'null')

        invalid_data['last_name'] = ''
        response = client.post(reverse('employees-list'), json.dumps(invalid_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check if ErrorDetail's code is returned properly
        self.assertEqual(response.data['last_name'][0].code, 'blank')

        invalid_data['last_name'] = self.last_name_max_len * 'x' + 'x'
        response = client.post(reverse('employees-list'), json.dumps(invalid_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check if ErrorDetail's code is returned properly
        self.assertEqual(response.data['last_name'][0].code, 'max_length')

    def test_post_invalid_abbreviation(self):
        # try to create one record with invalid data for abbreviation
        invalid_data = self.valid_data

        invalid_data['abbreviation'] = None
        response = client.post(reverse('employees-list'), json.dumps(invalid_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check if ErrorDetail's code is returned properly
        self.assertEqual(response.data['abbreviation'][0].code, 'null')

        invalid_data['abbreviation'] = ''
        response = client.post(reverse('employees-list'), json.dumps(invalid_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check if ErrorDetail's code is returned properly
        self.assertEqual(response.data['abbreviation'][0].code, 'blank')

        invalid_data['abbreviation'] = self.abbreviation_max_len * 'x' + 'x'
        response = client.post(reverse('employees-list'), json.dumps(invalid_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check if ErrorDetail's code is returned properly
        self.assertEqual(response.data['abbreviation'][0].code, 'max_length')

    def test_post_invalid_degree(self):
        # try to create one record with invalid data for degree
        invalid_data = self.valid_data

        invalid_data['degree'] = None
        response = client.post(reverse('employees-list'), json.dumps(invalid_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check if ErrorDetail's code is returned properly
        self.assertEqual(response.data['degree'][0].code, 'null')

        invalid_data['degree'] = 'x'
        response = client.post(reverse('employees-list'), json.dumps(invalid_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check if ErrorDetail's code is returned properly
        self.assertEqual(response.data['degree'][0].code, 'no_match')

    def test_post_invalid_position(self):
        # try to create one record with invalid data for position
        invalid_data = self.valid_data

        invalid_data['position'] = None
        response = client.post(reverse('employees-list'), json.dumps(invalid_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check if ErrorDetail's code is returned properly
        self.assertEqual(response.data['position'][0].code, 'null')

        invalid_data['position'] = 'x'
        response = client.post(reverse('employees-list'), json.dumps(invalid_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check if ErrorDetail's code is returned properly
        self.assertEqual(response.data['position'][0].code, 'no_match')

    def test_post_invalid_email(self):
        # try to create one record with invalid data for email
        invalid_data = self.valid_data

        invalid_data['e_mail'] = None
        response = client.post(reverse('employees-list'), json.dumps(invalid_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check if ErrorDetail's code is returned properly
        self.assertEqual(response.data['e_mail'][0].code, 'null')

        invalid_data['e_mail'] = ''
        response = client.post(reverse('employees-list'), json.dumps(invalid_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check if ErrorDetail's code is returned properly
        self.assertEqual(response.data['e_mail'][0].code, 'blank')

        invalid_data['e_mail'] = self.e_mail_max_len * 'x' + '@x.xx'
        response = client.post(reverse('employees-list'), json.dumps(invalid_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check if ErrorDetail's code is returned properly
        self.assertEqual(response.data['e_mail'][0].code, 'max_length')

        invalid_data['e_mail'] = 'x'
        response = client.post(reverse('employees-list'), json.dumps(invalid_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check if ErrorDetail's code is returned properly
        self.assertEqual(response.data['e_mail'][0].code, 'invalid')

        invalid_data['e_mail'] = 'xx@'
        response = client.post(reverse('employees-list'), json.dumps(invalid_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check if ErrorDetail's code is returned properly
        self.assertEqual(response.data['e_mail'][0].code, 'invalid')

        invalid_data['e_mail'] = '@x.xx'
        response = client.post(reverse('employees-list'), json.dumps(invalid_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check if ErrorDetail's code is returned properly
        self.assertEqual(response.data['e_mail'][0].code, 'invalid')

        invalid_data['e_mail'] = 'x@x.x'
        response = client.post(reverse('employees-list'), json.dumps(invalid_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check if ErrorDetail's code is returned properly
        self.assertEqual(response.data['e_mail'][0].code, 'invalid')

    def test_post_invalid_supervisor(self):
        # try to create one record with invalid data for supervisor
        invalid_data = self.valid_data

        invalid_data['supervisor'] = 'x'
        response = client.post(reverse('employees-list'), json.dumps(invalid_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check if ErrorDetail's code is returned properly
        self.assertEqual(response.data['supervisor'][0].code, 'no_match')

    def test_post_invalid_year_of_studies(self):
        # try to create one record with invalid data for supervisor
        invalid_data = self.valid_data

        invalid_data['year_of_studies'] = -.01
        response = client.post(reverse('employees-list'), json.dumps(invalid_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check if ErrorDetail's code is returned properly
        self.assertEqual(response.data['year_of_studies'][0].code, 'invalid', 'Value lower than 0')

        invalid_data['year_of_studies'] = .5
        response = client.post(reverse('employees-list'), json.dumps(invalid_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check if ErrorDetail's code is returned properly
        self.assertEqual(response.data['year_of_studies'][0].code, 'invalid', 'Value is not integer')
