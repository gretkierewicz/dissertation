from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueValidator
from rest_framework_nested.relations import NestedHyperlinkedRelatedField
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer

from employees.models import Employees
from modules.models import Classes
from schedules.models import Pensum, Schedules
from utils.relations import AdvNestedHyperlinkedIdentityField, ParentHiddenRelatedField
from utils.serializers import SerializerLambdaField
from .models import Orders, Plans, get_plans_additional_hours


class ScheduledEmployeesField(SlugRelatedField):
    """
    Schedules Employees Field to filter queryset for proper employees from current schedule
    """

    def get_queryset(self):
        # get plans filtered with url kwargs
        plans = Plans.objects.filter(
            order__classes__module__schedule__slug=self.context.get('request').resolver_match.kwargs.get(
                'schedule_slug'),
            order__classes__module__module_code=self.context.get('request').resolver_match.kwargs.get(
                'module_module_code'),
            order__classes__name=self.context.get('request').resolver_match.kwargs.get(
                'classes_name')
        )
        # exclude plan's instance so it's employee can be present in Form
        if self.root.instance:
            plans = plans.exclude(employee=self.root.instance.employee)
        pensums = Schedules.objects.get(
            slug=self.context.get('request').resolver_match.kwargs.get('schedule_slug')
        ).pensums.all()
        # exclude pensums with no more free hours
        pensums = [pensum for pensum in pensums if pensum.amount_until_contact_hours_limit >= 1]
        # return only employees possible to be chosen
        return self.queryset.filter(pensums__in=pensums).exclude(plans__in=plans)


class PlansSerializer(NestedHyperlinkedModelSerializer):
    """
    Plans Serializer - Basic serializer, nested inside Orders Serializer.
    """

    class Meta:
        model = Plans
        fields = ['url', 'employee_url', 'employee', 'plan_hours', 'plan_additional_hours',
                  # hidden
                  'order']
        extra_kwargs = {
            'plan_hours': {'min_value': 0}
        }

    # setting parents' URL kwargs
    parent_lookup_kwargs = {
        'schedule_slug': 'order__classes__module__schedule__slug',
        'module_module_code': 'order__classes__module__module_code',
        'classes_name': 'order__classes__name',
    }

    url = AdvNestedHyperlinkedIdentityField(
        view_name='classes-order-plans-detail',
        lookup_field=None,
        parent_lookup_kwargs={
            **parent_lookup_kwargs,
            'employee': 'employee__abbreviation'
        }
    )

    employee_url = AdvNestedHyperlinkedIdentityField(
        view_name='employees-detail',
        lookup_field=None,
        parent_lookup_kwargs={
            'abbreviation': 'employee__abbreviation'
        }
    )
    employee = ScheduledEmployeesField(slug_field='abbreviation', queryset=Employees.objects.all())

    # hidden field to establish current parent from URL
    order = ParentHiddenRelatedField(
        queryset=Orders.objects.all(),
        parent_lookup_kwargs={
            'schedule_slug': 'classes__module__schedule__slug',
            'module_module_code': 'classes__module__module_code',
            'classes_name': 'classes__name',
        }
    )

    def validate_plan_hours(self, data):
        max_value_to_set = reason = None

        # prevent exceeding order's hours number by its plans summary hours
        # TODO: in case of importing orders with nested plans, order instance needs to be passed with initial_data
        url_kwargs = self.context['request'].resolver_match.kwargs
        # get filter kwargs from request's URL
        order_filter_kwargs = {
            'classes__module__schedule__slug': url_kwargs['schedule_slug'],
            'classes__module__module_code': url_kwargs['module_module_code'],
            'classes__name': url_kwargs['classes_name']}
        # finding parent order instance
        order = get_object_or_404(Orders, **order_filter_kwargs)
        tmp = order.order_hours - order.plans_sum_hours + (self.instance.plan_hours if self.instance else 0)
        if data > tmp:
            max_value_to_set = tmp
            reason = "Order's hours number cannot be exceeded by summary number of its plans hours."

        # prevent exceeding employee's pensum maximum contact hours
        # get filter kwargs from request's URL
        pensum_filter_kwargs = {
            'schedule__slug': url_kwargs['schedule_slug'],
            'employee__abbreviation': self.initial_data.get('employee')}
        # finding employee's pensum instance
        pensum = get_object_or_404(Pensum, **pensum_filter_kwargs)
        tmp = pensum.amount_until_contact_hours_limit + (self.instance.plan_hours if self.instance else 0)
        if data > tmp and (not max_value_to_set or max_value_to_set > tmp):
            max_value_to_set = tmp
            reason = "Employee's pensum contact hours limit cannot be exceeded."

        # prevent exceeding employee's pensum additional hours limit
        factor = get_plans_additional_hours(order.classes.module,  1)
        tmp = (pensum.amount_until_over_time_hours_limit / (factor + 1)) + (
            self.instance.plan_hours if self.instance else 0)
        if data > tmp and (not max_value_to_set or max_value_to_set > tmp):
            max_value_to_set = tmp
            reason = "Employee's pensum additional hours limit cannot be exceeded."

        if max_value_to_set:
            raise ValidationError(f"Max. value possible: {int(max_value_to_set)}."
                                  f"{' Reason: {}'.format(reason) if reason else ''}")
        return data


class OrdersSerializer(NestedHyperlinkedModelSerializer):
    """
    Orders Serializer - basic one used for creating orders from modules list view and displaying created context.
    """

    class Meta:
        model = Orders
        fields = ['url', 'module', 'module_url', 'classes_name', 'classes_url',
                  'students_number', 'groups_number', 'order_hours', 'order_number',
                  'plans_url', 'plans_sum_hours', 'plans',
                  # write only
                  'classes']
        extra_kwargs = {
            'students_number': {'min_value': 0}
        }

    parent_lookup_kwargs = {
        'schedule_slug': 'classes__module__schedule__slug',
        'module_module_code': 'classes__module__module_code',
        'classes_name': 'classes__name'
    }

    url = AdvNestedHyperlinkedIdentityField(
        view_name='classes-order-detail',
        lookup_field=None,
        parent_lookup_kwargs=parent_lookup_kwargs
    )

    module = CharField(source='classes.module', read_only=True)
    module_url = AdvNestedHyperlinkedIdentityField(
        view_name='modules-detail',
        lookup_field=None,
        parent_lookup_kwargs={
            'schedule_slug': 'classes__module__schedule__slug',
            'module_code': 'classes__module__module_code',
        }
    )

    classes_name = CharField(source='classes.name', read_only=True)
    classes_url = AdvNestedHyperlinkedIdentityField(
        view_name='classes-detail',
        lookup_field=None,
        parent_lookup_kwargs={
            'schedule_slug': 'classes__module__schedule__slug',
            'module_module_code': 'classes__module__module_code',
            'name': 'classes__name'
        }
    )

    plans_url = AdvNestedHyperlinkedIdentityField(
        view_name='classes-order-plans-list',
        lookup_field=None,
        parent_lookup_kwargs=parent_lookup_kwargs
    )

    plans = PlansSerializer(read_only=True, many=True)

    classes = NestedHyperlinkedRelatedField(
        queryset=Classes.objects.filter(order__isnull=True),
        write_only=True,
        view_name='classes-detail',
        lookup_field='name',
        parent_lookup_kwargs={
            'schedule_slug': 'module__schedule__slug',
            'module_module_code': 'module__module_code'
        },
        validators=[UniqueValidator(queryset=Orders.objects.all())],
    )

    # this is magic method for FORM auto-generation
    def __iter__(self):
        # Additional filtering for classes' list:
        if self.fields.get('classes'):
            self.fields['classes'].queryset = self.fields['classes'].queryset.filter(
                module__schedule__slug=self.context['request'].resolver_match.kwargs.get('schedule_slug'))
        # standard procedure:
        for field in self.fields.values():
            yield self[field.field_name]


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

    classes = ParentHiddenRelatedField(
        queryset=Classes.objects.all(),
        parent_lookup_kwargs={
            'schedule_slug': 'module__schedule__slug',
            'module_module_code': 'module__module_code',
            'classes_name': 'name'
        }
    )


class EmployeePlansSerializer(PlansSerializer):
    class Meta:
        model = Plans
        fields = ['url', 'module_code', 'classes_name', 'order_hours', 'plans_sum_hours', 'employee_plan_hours']
        extra_kwargs = {
            'url': {'view_name': 'classes-order-plans-detail', 'lookup_field': 'employee'},
        }

    module_code = SerializerLambdaField(lambda obj: obj.order.classes.module.module_code)
    classes_name = SerializerLambdaField(lambda obj: obj.order.classes.name)
    order_hours = SerializerLambdaField(lambda obj: obj.order.order_hours)
    plans_sum_hours = SerializerLambdaField(lambda obj: obj.order.plans_sum_hours)
    employee_plan_hours = SerializerLambdaField(lambda obj: obj.plan_hours)
