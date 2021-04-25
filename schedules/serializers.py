from rest_framework.exceptions import ValidationError
from rest_framework.relations import HyperlinkedIdentityField, SlugRelatedField, StringRelatedField
from rest_framework.serializers import ModelSerializer
from rest_framework_nested.relations import NestedHyperlinkedIdentityField
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer

from AGH.AGH_utils import AdditionalHoursFactorData
from employees.models import Employees
from orders.serializers import EmployeePlansSerializer
from utils.relations import AdvNestedHyperlinkedIdentityField, ParentHiddenRelatedField
from .models import Pensum, PensumAdditionalHoursFactors, PensumBasicThresholdFactors, PensumReductions, Schedules


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


class PensumBasicThresholdFactorSerializer(NestedHyperlinkedModelSerializer):
    class Meta:
        model = PensumBasicThresholdFactors
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


class PensumAdditionalHoursFactorsSerializer(NestedHyperlinkedModelSerializer):
    class Meta:
        model = PensumAdditionalHoursFactors
        fields = ['url', 'name', 'value_per_unit', 'amount', 'description',
                  # hidden
                  'pensum']
        extra_kwargs = {
            'value_per_unit': {'min_value': 1},
            'amount': {'min_value': 1, 'initial': 1}
        }

    parent_lookup_kwargs = {
        'schedule_slug': 'pensum__schedule__slug',
        'pensums_employee': 'pensum__employee__abbreviation'
    }
    url = NestedHyperlinkedIdentityField(
        view_name='pensum-additional_hours_factors-detail',
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

    def validate_value_per_unit(self, value):
        # create class with additional data regarding name of the factor
        factor_data = AdditionalHoursFactorData(self.initial_data.get('name'))
        if not factor_data.group_ID:
            # get filter kwargs from request's URL and search for similar factors for this pensum
            url_kwargs = self.context['request'].resolver_match.kwargs
            filter_kwargs = {
                'pensum__schedule__slug': url_kwargs['schedule_slug'],
                'pensum__employee__abbreviation': url_kwargs['pensums_employee'],
                'name': self.initial_data.get('name'),
            }
            other_factors = PensumAdditionalHoursFactors.objects.filter(**filter_kwargs)
            if self.instance:
                other_factors = other_factors.exclude(pk=self.instance.pk)
            similar_factors_hours = sum([item.amount * item.value_per_unit for item in other_factors])

            limit = factor_data.limit_per_unit
            # TODO: consider replacing this simple logic of doubling semester limits
            if factor_data.limit_key_name.split()[-1] == 'semester':
                limit *= 2

            if value * int(self.initial_data.get('amount')) > limit - similar_factors_hours:
                raise ValidationError(
                    f"Value exceeds limit per year for this factor. Maximum value to be set with this amount: "
                    f"{(limit - similar_factors_hours) // int(self.initial_data.get('amount'))}. "
                    f"Hours until limit (value * amount): {limit - similar_factors_hours}."
                )
        if value > factor_data.limit_per_unit:
            raise ValidationError(
                f"Value exceeds limit per unit for this factor. Maximum value to be set: "
                f"{factor_data.limit_per_unit}"
            )
        return value

    def validate_amount(self, value):
        # create class with additional data regarding name of the factor
        factor_data = AdditionalHoursFactorData(self.initial_data.get('name'))
        if factor_data.group_ID:
            # get filter kwargs from request's URL and search for similar factors for this pensum
            url_kwargs = self.context['request'].resolver_match.kwargs
            filter_kwargs = {
                'pensum__schedule__slug': url_kwargs['schedule_slug'],
                'pensum__employee__abbreviation': url_kwargs['pensums_employee'],
                'name': self.initial_data.get('name'),
            }
            other_factors = PensumAdditionalHoursFactors.objects.filter(**filter_kwargs)
            if self.instance:
                other_factors = other_factors.exclude(pk=self.instance.pk)

            similar_factors_amount = sum([item.amount for item in other_factors])
            free_amount_to_use = factor_data.max_amount_for_group - similar_factors_amount
            if value > free_amount_to_use:
                raise ValidationError(
                    f"Value exceeds limit per year for this factor's group. Maximum value to be set: "
                    f"{free_amount_to_use}"
                )
        return value


class PensumSerializer(NestedHyperlinkedModelSerializer):
    class Meta:
        model = Pensum
        fields = ['url', 'employee_url', 'first_name', 'last_name', 'employee', 'e_mail', 'pensum_group',
                  'basic_threshold', 'part_of_job_time', 'basic_threshold_factors_url', 'basic_threshold_factors',
                  'reduction_url', 'reduction', 'calculated_threshold',
                  'pensum_contact_hours', 'plans',
                  'additional_hours_factors_url', 'additional_hours_factors',
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

    employee_url = AdvNestedHyperlinkedIdentityField(
        view_name='employees-detail',
        lookup_field=None,
        parent_lookup_kwargs={
            'abbreviation': 'employee__abbreviation'
        }
    )
    first_name = StringRelatedField(read_only=True, source='employee.first_name')
    last_name = StringRelatedField(read_only=True, source='employee.last_name')
    employee = SlugRelatedField(queryset=Employees.objects.all(), slug_field='abbreviation')
    e_mail = StringRelatedField(read_only=True, source='employee.e_mail')
    pensum_group = StringRelatedField(read_only=True, source='employee.pensum_group')

    part_of_job_time = StringRelatedField(read_only=True, source='employee.part_of_job_time')
    basic_threshold_factors_url = NestedHyperlinkedIdentityField(
        view_name='pensum-factors-list',
        lookup_field='employee',
        lookup_url_kwarg='pensums_employee',
        parent_lookup_kwargs=parent_lookup_kwargs
    )
    basic_threshold_factors = PensumBasicThresholdFactorSerializer(read_only=True, many=True)
    reduction_url = NestedHyperlinkedIdentityField(
        view_name='pensum-reduction-detail',
        lookup_field='employee',
        lookup_url_kwarg='pensums_employee',
        parent_lookup_kwargs=parent_lookup_kwargs
    )
    reduction = PensumReductionSerializer(read_only=True)

    plans = EmployeePlansSerializer(many=True, read_only=True, source='employee.plans')

    additional_hours_factors_url = NestedHyperlinkedIdentityField(
        view_name='pensum-additional_hours_factors-list',
        lookup_field='employee',
        lookup_url_kwarg='pensums_employee',
        parent_lookup_kwargs=parent_lookup_kwargs
    )
    additional_hours_factors = PensumAdditionalHoursFactorsSerializer(many=True, read_only=True)

    schedule = ParentHiddenRelatedField(
        queryset=Schedules.objects.all(),
        parent_lookup_kwargs={
            'schedule_slug': 'slug'
        },
    )
