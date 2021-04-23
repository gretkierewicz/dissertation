from rest_framework.relations import HyperlinkedIdentityField, SlugRelatedField, StringRelatedField
from rest_framework.serializers import ModelSerializer
from rest_framework_nested.relations import NestedHyperlinkedIdentityField
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer

from employees.models import Employees
from orders.serializers import EmployeePlansSerializer
from utils.relations import AdvNestedHyperlinkedIdentityField, ParentHiddenRelatedField
from .models import Pensum, PensumFactors, PensumReductions, Schedules


class ScheduleSerializer(ModelSerializer):
    class Meta:
        model = Schedules
        fields = ['url', 'slug', 'modules_url', 'orders_url', 'pensums_url']

    url = HyperlinkedIdentityField(view_name='schedules-detail', lookup_field='slug')

    modules_url = HyperlinkedIdentityField(
        view_name='modules-list',
        lookup_field='slug',
        lookup_url_kwarg='schedule_slug'
    )
    orders_url = HyperlinkedIdentityField(
        view_name='orders-list',
        lookup_field='slug',
        lookup_url_kwarg='schedule_slug'
    )
    pensums_url = HyperlinkedIdentityField(
        view_name='pensums-list',
        lookup_field='slug',
        lookup_url_kwarg='schedule_slug'
    )


class PensumFactorSerializer(NestedHyperlinkedModelSerializer):
    class Meta:
        model = PensumFactors
        fields = ['url', 'pk', 'name', 'factor_type', 'value',
                  # hidden
                  'pensum']

    parent_lookup_kwargs = {
        'schedule_slug': 'pensum__schedule__slug',
        'pensums_employee': 'pensum__employee__abbreviation'
    }
    url = NestedHyperlinkedIdentityField(
        view_name='pensum-factors-detail',
        lookup_field='pk',
        parent_lookup_kwargs=parent_lookup_kwargs
    )

    pensum = ParentHiddenRelatedField(
        queryset=Pensum.objects.all(),
        parent_lookup_kwargs={
            'schedule_slug': 'schedule__slug',
            'pensums_employee': 'employee__abbreviation'
        }
    )


class PensumReductionSerializer(NestedHyperlinkedModelSerializer):
    class Meta:
        model = PensumReductions
        fields = ['function', 'reduction_value',
                  # hidden
                  'pensum']

    parent_lookup_kwargs = {
        'schedule_slug': 'pensum__schedule__slug',
        'pensums_employee': 'pensum__employee__abbreviation'
    }

    pensum = ParentHiddenRelatedField(
        queryset=Pensum.objects.all(),
        parent_lookup_kwargs={
            'schedule_slug': 'schedule__slug',
            'pensums_employee': 'employee__abbreviation'
        }
    )


class PensumSerializer(NestedHyperlinkedModelSerializer):
    class Meta:
        model = Pensum
        fields = ['url', 'employee_url', 'first_name', 'last_name', 'employee', 'e_mail', 'pensum_group', 'plans',
                  'planned_pensum_hours', 'calculated_threshold', 'basic_threshold',
                  'factors_url', 'factors', 'reduction_url', 'reduction',
                  # hidden
                  'schedule']
        extra_kwargs = {
            'value': {'read_only': True}
        }

    parent_lookup_kwargs = {
        'schedule_slug': 'schedule__slug'
    }
    url = NestedHyperlinkedIdentityField(
        view_name='pensums-detail',
        lookup_field='employee',
        parent_lookup_kwargs=parent_lookup_kwargs
    )

    pensum_group = StringRelatedField(read_only=True, source='employee.pensum_group')

    employee_url = AdvNestedHyperlinkedIdentityField(
        view_name='employees-detail',
        lookup_field=None,
        parent_lookup_kwargs={
            'abbreviation': 'employee__abbreviation'
        }
    )
    employee = SlugRelatedField(queryset=Employees.objects.all(), slug_field='abbreviation')

    plans = EmployeePlansSerializer(many=True, read_only=True, source='employee.plans')

    factors_url = NestedHyperlinkedIdentityField(
        view_name='pensum-factors-list',
        lookup_field='employee',
        lookup_url_kwarg='pensums_employee',
        parent_lookup_kwargs=parent_lookup_kwargs
    )
    factors = PensumFactorSerializer(read_only=True, many=True)

    reduction_url = NestedHyperlinkedIdentityField(
        view_name='pensum-reduction-detail',
        lookup_field='employee',
        lookup_url_kwarg='pensums_employee',
        parent_lookup_kwargs=parent_lookup_kwargs
    )
    reduction = PensumReductionSerializer(read_only=True)

    schedule = ParentHiddenRelatedField(
        queryset=Schedules.objects.all(),
        parent_lookup_kwargs={
            'schedule_slug': 'slug'
        },
    )
