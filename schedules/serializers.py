from rest_framework.relations import HyperlinkedIdentityField, SlugRelatedField
from rest_framework_nested.relations import NestedHyperlinkedIdentityField
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer

from employees.models import Employees
from utils.relations import ParentHiddenRelatedField
from .models import Schedules, Pensum, PensumFactors, PensumReductions
from modules.serializers import ModuleSerializer


class ScheduleSerializer(ModuleSerializer):
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
        fields = ['url', 'function', 'reduction_value',
                  # hidden
                  'pensum']

    parent_lookup_kwargs = {
        'schedule_slug': 'pensum__schedule__slug',
        'pensums_employee': 'pensum__employee__abbreviation'
    }
    url = NestedHyperlinkedIdentityField(
        view_name='pensum-reductions-detail',
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


class PensumSerializer(NestedHyperlinkedModelSerializer):
    class Meta:
        model = Pensum
        fields = ['url', 'employee_url', 'employee', 'planned_pensum_hours',
                  'calculated_threshold', 'basic_threshold',
                  'factors_url', 'factors', 'reductions_url', 'reductions',
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

    employee_url = HyperlinkedIdentityField(
        view_name='employees-detail',
        lookup_field='employee',
        lookup_url_kwarg='abbreviation'
    )
    employee = SlugRelatedField(queryset=Employees.objects.all(), slug_field='abbreviation')

    factors_url = NestedHyperlinkedIdentityField(
        view_name='pensum-factors-list',
        lookup_field='employee',
        lookup_url_kwarg='pensums_employee',
        parent_lookup_kwargs=parent_lookup_kwargs
    )
    factors = PensumFactorSerializer(read_only=True, many=True)

    reductions_url = NestedHyperlinkedIdentityField(
        view_name='pensum-reductions-list',
        lookup_field='employee',
        lookup_url_kwarg='pensums_employee',
        parent_lookup_kwargs=parent_lookup_kwargs
    )
    reductions = PensumReductionSerializer(read_only=True, many=True)

    schedule = ParentHiddenRelatedField(
        queryset=Schedules.objects.all(),
        parent_lookup_kwargs={
            'schedule_slug': 'slug'
        },
    )
