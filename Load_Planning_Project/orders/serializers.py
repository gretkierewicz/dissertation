from rest_framework.relations import HyperlinkedIdentityField, SlugRelatedField
from rest_framework.serializers import ModelSerializer
from rest_framework.validators import UniqueValidator
from rest_framework_nested.relations import NestedHyperlinkedRelatedField
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer

from employees.models import Employees
from modules.models import Classes
from utils.serializers import GetParentHiddenField

from .models import Orders, Plans


class OrderPlansSerializer(NestedHyperlinkedModelSerializer):
    class Meta:
        model = Plans
        fields = ['url', 'employee', 'plan_hours',
                  # hidden
                  'order']
        extra_kwargs = {
            'url': {'view_name': 'order-plans-detail', 'lookup_field': 'employee'},
            'employee': {'lookup_field': 'abbreviation'},
            'plan_hours': {'min_value': 0}
        }
    # setting parents' URL kwargs
    parent_lookup_kwargs = {
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


class OrderSerializer(ModelSerializer):
    class Meta:
        model = Orders
        fields = ['url', 'classes', 'students_number', 'groups_number', 'order_hours', 'order_number',
                  'plans_url', 'plans']
        extra_kwargs = {
            'students_number': {'min_value': 0}
        }

    url = HyperlinkedIdentityField(view_name='orders-detail')

    plans_url = HyperlinkedIdentityField(
        view_name='order-plans-list',
        lookup_field='pk',
        lookup_url_kwarg='order_pk'
    )
    plans = OrderPlansSerializer(read_only=True, many=True)

    classes = NestedHyperlinkedRelatedField(
        queryset=Classes.objects.all(),
        view_name='classes-detail',
        lookup_field='name',
        parent_lookup_kwargs={
            'module_module_code': 'module__module_code'
        },
        validators=[UniqueValidator(queryset=Orders.objects.all())],
    )
