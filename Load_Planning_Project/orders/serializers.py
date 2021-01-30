from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueValidator
from rest_framework_nested.relations import NestedHyperlinkedRelatedField, NestedHyperlinkedIdentityField
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer

from employees.models import Employees
from modules.models import Classes
from utils.serializers import GetParentHiddenField

from .models import Orders, Plans


class PlansSerializer(NestedHyperlinkedModelSerializer):
    class Meta:
        model = Plans
        fields = ['url', 'employee', 'plan_hours',
                  # hidden
                  'order']
        extra_kwargs = {
            'url': {'view_name': 'class-order-plans-detail', 'lookup_field': 'employee'},
            'employee': {'lookup_field': 'abbreviation'},
            'plan_hours': {'min_value': 0}
        }
    # setting parents' URL kwargs
    parent_lookup_kwargs = {
        'module_module_code': 'order__classes__module__module_code',
        'class_name': 'order__classes__name',
        'order_pk': 'order__pk'
    }

    employee = SlugRelatedField(slug_field='abbreviation', queryset=Employees.objects.all())

    # hidden field to establish current parent from URL
    order = GetParentHiddenField(
        queryset=Orders.objects.all(),
        matches={
            'order_pk': 'pk'
        }
    )


class OrdersSerializer(NestedHyperlinkedModelSerializer):
    class Meta:
        model = Orders
        fields = ['url', 'classes', 'students_number', 'groups_number', 'order_hours', 'order_number',
                  'plans_url', 'plans']
        extra_kwargs = {
            'url': {'view_name': 'class-order-detail'},
            'students_number': {'min_value': 0}
        }
    parent_lookup_kwargs = {
        'module_module_code': 'classes__module__module_code',
        'class_name': 'classes__name'
    }

    plans_url = NestedHyperlinkedIdentityField(
        view_name='class-order-plans-list',
        lookup_field='pk',
        lookup_url_kwarg='order_pk',
        parent_lookup_kwargs={
            'module_module_code': 'classes__module__module_code',
            'class_name': 'classes__name'
        }
    )
    plans = PlansSerializer(read_only=True, many=True)

    classes = NestedHyperlinkedRelatedField(
        queryset=Classes.objects.filter(order__isnull=True),
        view_name='classes-detail',
        lookup_field='name',
        parent_lookup_kwargs={
            'module_module_code': 'module__module_code'
        },
        validators=[UniqueValidator(queryset=Orders.objects.all())],
    )


class ClassesOrderSerializer(OrdersSerializer):
    class Meta:
        model = Orders
        fields = ['url', 'students_number', 'groups_number', 'order_hours', 'order_number',
                  'plans_url', 'plans',
                  # hidden
                  'classes']
        extra_kwargs = {
            'url': {'view_name': 'class-order-detail'}
        }

    classes = GetParentHiddenField(
        queryset=Classes.objects.all(),
        matches={
            'module_module_code': 'module__module_code',
            'class_name': 'name'
        }
    )
