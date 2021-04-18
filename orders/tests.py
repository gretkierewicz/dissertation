import json
import random

from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APIRequestFactory, APITestCase

from employees.models import Degrees, Employees, Positions
from employees.tests import EmployeeFields
from modules.models import CLASSES_NAMES, Classes, Modules
from modules.serializers import ClassSerializer
from utils.random_generators import random_max_len_field_str, random_str
from utils.tests import BasicAPITests
from .models import Orders
from .serializers import ClassesOrderSerializer, OrdersSerializer

client = APIClient()
factory = APIRequestFactory()


class OrdersFields:
    classes = 'classes'
    students_number = 'students_number'
    order_number = 'order_number'


class OrdersTests(BasicAPITests, APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.factory = APIRequestFactory()

        cls.model = Orders
        cls.serializer = ClassesOrderSerializer
        cls.list_serializer = OrdersSerializer
        cls.list_view_name = 'orders-list'
        cls.detail_view_name = 'classes-order-detail'
        cls.context = {'request': cls.factory.get(reverse(cls.list_view_name), format=json)}
        cls.lookup = {
            'classes__module__module_code': r'[\w]+/modules/(?P<classes__module__module_code>[\w]+)/',
            'classes__name__startswith': r'[\w]+/classes/(?P<classes__name__startswith>[\w]+)',
        }
        cls.field_lookup = 'classes'
        cls.delete_forbidden = False

        def create_employee():
            return Employees.objects.create(**{
                EmployeeFields.first_name: random_max_len_field_str(Employees, EmployeeFields.first_name),
                EmployeeFields.last_name: random_max_len_field_str(Employees, EmployeeFields.last_name),
                EmployeeFields.abbreviation: random_max_len_field_str(Employees, EmployeeFields.abbreviation),
                EmployeeFields.e_mail: random_max_len_field_str(Employees, EmployeeFields.e_mail)[:-6] + '@ab.ba',
                EmployeeFields.degree: Degrees.objects.create(name=random_str(5)),
                EmployeeFields.position: Positions.objects.create(name=random_str(5))
            })

        module_obj = Modules.objects.create(**{
            'module_code': random_max_len_field_str(Modules, 'module_code'),
            'name': random_max_len_field_str(Modules, 'name'),
            'supervisor': create_employee(),
        })
        classes_obj = Classes.objects.create(**{
            'module': module_obj,
            'name': random.choice(CLASSES_NAMES),
            'classes_hours': random.randint(10, 20)
        })
        cls.obj_parent_url_kwargs = {
            'module_module_code': module_obj.module_code,
            'classes_name': classes_obj.name,
        }
        cls.obj_parent_get_kwargs = {
            'classes__module__module_code': module_obj.module_code,
            'classes__name': classes_obj.name,
        }
        cls.obj = Orders.objects.create(**{
            OrdersFields.classes: classes_obj,
            OrdersFields.students_number: random.randint(1, 200)
        })

        diff_names = CLASSES_NAMES.copy()
        diff_names.remove(classes_obj.name)
        diff_classes_obj = Classes.objects.create(**{
            'module': module_obj,
            'name': random.choice(diff_names),
            'classes_hours': random.randint(10, 20)
        })
        cls.valid_post_data_payload = {
            'min data': {
                OrdersFields.classes: ClassSerializer(
                    instance=diff_classes_obj, context=cls.context).data.get('url'),
                OrdersFields.students_number: random.randint(1, 200)
            }
        }
        diff_names.remove(diff_classes_obj.name)
        another_diff_classes_obj = Classes.objects.create(**{
            'module': module_obj,
            'name': random.choice(diff_names),
            'classes_hours': random.randint(10, 20)
        })
        cls.valid_post_data_payload['full data'] = {
            OrdersFields.classes: ClassSerializer(
                instance=another_diff_classes_obj, context=cls.context).data.get('url'),
            OrdersFields.students_number: random.randint(1, 200),
            OrdersFields.order_number: random_max_len_field_str(cls.model, OrdersFields.order_number)
        }

        cls.valid_put_data_payload = {
            'min ' + OrdersFields.students_number: {
                OrdersFields.students_number: 1,
                OrdersFields.order_number: random_max_len_field_str(cls.model, OrdersFields.order_number)},
            'high ' + OrdersFields.students_number: {
                OrdersFields.students_number: 2000, OrdersFields.order_number:
                    random_max_len_field_str(cls.model, OrdersFields.order_number)},
            'max length ' + OrdersFields.order_number: {
                OrdersFields.students_number: random.randint(1, 200),
                OrdersFields.order_number: random_max_len_field_str(cls.model, OrdersFields.order_number)},
            'short ' + OrdersFields.order_number: {
                OrdersFields.students_number: random.randint(1, 200), OrdersFields.order_number: random_str(1)},
            'empty ' + OrdersFields.order_number: {
                OrdersFields.students_number: random.randint(1, 200), OrdersFields.order_number: ''},
            'null ' + OrdersFields.order_number: {
                OrdersFields.students_number: random.randint(1, 200), OrdersFields.order_number: None}
        }
        cls.valid_partial_data = {
            'min ' + OrdersFields.students_number: {OrdersFields.students_number: 1},
            'high ' + OrdersFields.students_number: {OrdersFields.students_number: 2000},
            'max length ' + OrdersFields.order_number: {
                OrdersFields.order_number: random_max_len_field_str(cls.model, OrdersFields.order_number)},
            'short ' + OrdersFields.order_number: {OrdersFields.order_number: random_str(1)},
            'empty ' + OrdersFields.order_number: {OrdersFields.order_number: ''},
            'null ' + OrdersFields.order_number: {OrdersFields.order_number: None}
        }

        cls.invalid_post_data_payload = {
            'negative ' + OrdersFields.students_number: {
                OrdersFields.classes: ClassSerializer(instance=classes_obj, context=cls.context).data.get('url'),
                OrdersFields.students_number: -1,
                OrdersFields.order_number: random_max_len_field_str(cls.model, OrdersFields.order_number)},
            'empty ' + OrdersFields.students_number: {
                OrdersFields.classes: ClassSerializer(instance=classes_obj, context=cls.context).data.get('url'),
                OrdersFields.students_number: '',
                OrdersFields.order_number: random_max_len_field_str(cls.model, OrdersFields.order_number)},
            'too long ' + OrdersFields.order_number: {
                OrdersFields.classes: ClassSerializer(instance=classes_obj, context=cls.context).data.get('url'),
                OrdersFields.students_number: 12,
                OrdersFields.order_number:
                    random_max_len_field_str(cls.model, OrdersFields.order_number) + random_str(1)}
        }
        cls.invalid_put_data_payload = cls.invalid_post_data_payload.copy()
        for key in cls.invalid_put_data_payload.keys():
            cls.invalid_put_data_payload[key].pop('classes')
        cls.invalid_partial_data = {
            'negative ' + OrdersFields.students_number: {OrdersFields.students_number: -1},
            'empty ' + OrdersFields.students_number: {OrdersFields.students_number: ''},
            'null ' + OrdersFields.students_number: {OrdersFields.students_number: None},
            'too long ' + OrdersFields.order_number: {
                OrdersFields.order_number: random_max_len_field_str(
                    cls.model, OrdersFields.order_number) + random_str(1)}
        }
