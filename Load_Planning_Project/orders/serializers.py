from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueValidator
from rest_framework_nested.relations import NestedHyperlinkedRelatedField
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer

from employees.models import Employees
from modules.models import Classes
from utils.relations import AdvNestedHyperlinkedIdentityField
from utils.serializers import GetParentHiddenField

from .models import Orders, Plans


class PlansSerializer(NestedHyperlinkedModelSerializer):
    """
    Plans Serializer - Basic serializer, nested inside Orders Serializer.
    """
    class Meta:
        model = Plans
        fields = ['url', 'employee', 'plan_hours',
                  # hidden
                  'order']
        extra_kwargs = {
            'url': {'view_name': 'classes-order-plans-detail', 'lookup_field': 'employee'},
            'plan_hours': {'min_value': 0}
        }
    # setting parents' URL kwargs
    parent_lookup_kwargs = {
        'module_module_code': 'order__classes__module__module_code',
        'classes_name': 'order__classes__name',
    }

    employee = SlugRelatedField(slug_field='abbreviation', queryset=Employees.objects.all())

    # hidden field to establish current parent from URL
    order = GetParentHiddenField(
        queryset=Orders.objects.all(),
        matches={
            'module_module_code': 'classes__module__module_code',
            'classes_name': 'classes__name',
        }
    )

    def validate_plan_hours(self, data):
        # prevent exceeding order's hours number by its plans summary hours
        # TODO: in case of importing orders with nested plans, order instance needs to be passed with initial_data
        url_kwargs = self.context['request'].resolver_match.kwargs
        # get filter kwargs from request's URL
        filter_kwargs = {
            'classes__module__module_code': url_kwargs['module_module_code'],
            'classes__name': url_kwargs['classes_name']}
        # finding parent order instance
        order = get_object_or_404(Orders, **filter_kwargs)
        if order.plans_sum_hours - (self.instance.plan_hours if self.instance else 0) + data > order.order_hours:
            raise ValidationError(
                f"Order's hours number cannot be exceeded by summary number of its plans hours. "
                f"Maximum number of hours to set with {'this' if self.instance else 'new'} plan: "
                f"{order.order_hours - order.plans_sum_hours + (self.instance.plan_hours if self.instance else 0)}"
            )
        return data


class OrdersSerializer(NestedHyperlinkedModelSerializer):
    """
    Orders Serializer - basic one used for creating orders from modules list view and displaying created context.
    """
    class Meta:
        model = Orders
        fields = ['url', 'classes', 'students_number', 'groups_number', 'order_hours', 'order_number',
                  'plans_url', 'plans_sum_hours', 'plans']
        extra_kwargs = {
            'students_number': {'min_value': 0}
        }
    parent_lookup_kwargs = {
        'module_module_code': 'classes__module__module_code',
        'classes_name': 'classes__name'
    }
    url = AdvNestedHyperlinkedIdentityField(
        view_name='classes-order-detail',
        lookup_field=None,
        parent_lookup_kwargs=parent_lookup_kwargs
    )

    plans_url = AdvNestedHyperlinkedIdentityField(
        view_name='classes-order-plans-list',
        lookup_field=None,
        parent_lookup_kwargs=parent_lookup_kwargs
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
    """
    Classes Order Serializer - derivative of basic serializer.
    Created to be nested inside it's OneToOne relation object - CLasses instance
    """
    class Meta:
        model = Orders
        fields = ['url', 'students_number', 'groups_number', 'order_hours', 'order_number',
                  'plans_url', 'plans_sum_hours', 'plans',
                  # hidden
                  'classes']
        extra_kwargs = {
            'students_number': {'min_value': 0}
        }

    classes = GetParentHiddenField(
        queryset=Classes.objects.all(),
        matches={
            'module_module_code': 'module__module_code',
            'classes_name': 'name'
        }
    )
