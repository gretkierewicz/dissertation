import math

from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.relations import HyperlinkedIdentityField, SlugRelatedField, StringRelatedField
from rest_framework.serializers import ModelSerializer
from rest_framework_nested.relations import NestedHyperlinkedIdentityField
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer

from AGH.AGH_utils import AdditionalHoursFactorData, ExamsFactors, get_exam_hours
from employees.models import Employees
from modules.models import Modules
from orders.serializers import EmployeePlansSerializer
from utils.relations import AdvNestedHyperlinkedIdentityField, ParentHiddenRelatedField
from utils.serializers import SerializerLambdaField
from .models import ExamsAdditionalHours, Pensum, PensumAdditionalHoursFactors, PensumBasicThresholdFactors, \
    PensumReductions, Schedules


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
        fields = ['url', 'name', 'value_per_unit', 'amount', 'description', 'total_factor_hours_counted_into_limit',
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
        max_value_to_set = reason = None

        other_factors, factor_data = self.__get_additional_hours_factor_data()
        if not factor_data.group_ID and other_factors:
            similar_factors_hours = sum([item.amount * item.value_per_unit for item in other_factors])
            limit = factor_data.limit_per_unit
            # TODO: consider replacing this simple logic of doubling semester limits
            if factor_data.limit_key_name.split()[-1] == 'semester':
                limit *= 2
            tmp = (limit - similar_factors_hours) // int(self.initial_data.get('amount'))
            if value > tmp:
                max_value_to_set = int(tmp)
                reason = f"Value exceeds limit per year for this factor."

        if value > factor_data.limit_per_unit and (
                not max_value_to_set or max_value_to_set > factor_data.limit_per_unit
        ):
            max_value_to_set = factor_data.limit_per_unit
            reason = "Value exceeds limit per unit for this factor."

        # prevent exceeding employee pensum's additional hours limit
        url_kwargs = self.context['request'].resolver_match.kwargs
        # get filter kwargs from request's URL
        pensum_filter_kwargs = {
            'schedule__slug': url_kwargs['schedule_slug'],
            'employee__abbreviation': url_kwargs['pensums_employee']}
        # finding parent pensum instance
        pensum = get_object_or_404(Pensum, **pensum_filter_kwargs)
        tmp = pensum.amount_until_over_time_hours_limit + (self.instance.value_per_unit if self.instance else 0)
        if value > tmp:
            if not max_value_to_set or tmp < max_value_to_set:
                max_value_to_set = int(tmp)
                reason = "Value exceeds employee's pensum additional hours limit."

        if max_value_to_set:
            raise ValidationError(f"Max. value possible: {max_value_to_set}."
                                  f"{' Reason: {}'.format(reason) if reason else ''}")
        return value

    def validate_amount(self, value):
        other_factors, factor_data = self.__get_additional_hours_factor_data()
        if factor_data.group_ID and other_factors:
            similar_factors_amount = sum([item.amount for item in other_factors])
            free_amount_to_use = factor_data.max_amount_for_group - similar_factors_amount
            if value > free_amount_to_use:
                raise ValidationError(
                    f"Value exceeds limit per year for this factor's group. Maximum value to be set: "
                    f"{free_amount_to_use}"
                )
        return value

    def __get_additional_hours_factor_data(self):
        other_factors = None
        # create class with additional data regarding name of the factor
        additional_hours_factor_data = AdditionalHoursFactorData(self.initial_data.get('name'))
        if not additional_hours_factor_data.group_ID:
            # get filter kwargs from request's URL and search for similar factors for this pensum
            url_kwargs = self.context['request'].resolver_match.kwargs
            filter_kwargs = {
                'pensum__schedule__slug': url_kwargs['schedule_slug'],
                'pensum__employee__abbreviation': url_kwargs['pensums_employee'],
                'name': self.initial_data.get('name'),
            }
            other_factors = PensumAdditionalHoursFactors.objects.filter(**filter_kwargs)
        return (
            other_factors.exclude(pk=self.instance.pk) if self.instance else other_factors,
            additional_hours_factor_data
        )


class ModulesToSetupRelatedField(SlugRelatedField):
    """
    Modules related field excluding exams fully staffed
    """

    def get_queryset(self):
        schedule_slug = self.context.get('request').resolver_match.kwargs.get('schedule_slug')
        pensum = Pensum.objects.get(
            employee__abbreviation=self.context.get('request').resolver_match.kwargs.get('pensums_employee'),
            schedule__slug=schedule_slug
        )
        queryset = self.queryset.filter(schedule__slug=schedule_slug)
        # exclude modules with no orders at all (cannot simply exclude as main_order is a property)
        modules_pk_to_exclude = [module.pk for module in queryset if not module.main_order]
        # exclude employee's staffed exams
        modules_pk_to_exclude.extend([exam.module.pk for exam in pensum.exams_additional_hours.all()])
        # exclude already fully staffed exams
        for module in queryset:
            if module.exams_portion_staffed >= 1 and module.pk not in modules_pk_to_exclude:
                modules_pk_to_exclude.append(module.pk)
        # do not exclude instance if present
        if self.root.instance:
            modules_pk_to_exclude.remove(self.root.instance.module.pk)
        return queryset.exclude(pk__in=set(modules_pk_to_exclude))


class ExamsAdditionalHoursSerializer(NestedHyperlinkedModelSerializer):
    class Meta:
        model = ExamsAdditionalHours
        fields = ['url', 'module_url', 'module', 'module_name', 'students_number', 'type', 'portion',
                  'total_factor_hours',
                  # hidden
                  'pensum']
        extra_kwargs = {
            'url': {'view_name': 'pensum-exams_additional_hours-detail'},
            'portion': {'min_value': 0, 'max_value': 1, 'initial': 1}
        }

    parent_lookup_kwargs = {
        'schedule_slug': 'pensum__schedule__slug',
        'pensums_employee': 'pensum__employee__abbreviation'
    }

    module_url = AdvNestedHyperlinkedIdentityField(
        view_name='modules-detail',
        lookup_field=None,
        parent_lookup_kwargs={
            'schedule_slug': 'pensum__schedule__slug',
            'module_code': 'module__module_code'
        }
    )
    module = ModulesToSetupRelatedField(slug_field='module_code', queryset=Modules.objects.filter(examination=True))
    module_name = SerializerLambdaField(lambda obj: obj.module.name)
    students_number = SerializerLambdaField(
        lambda obj: obj.module.main_order.students_number if obj.module.main_order else None)

    pensum = ParentHiddenRelatedField(
        queryset=Pensum.objects.all(),
        parent_lookup_kwargs={
            'schedule_slug': 'schedule__slug',
            'pensums_employee': 'employee__abbreviation'
        }
    )

    def validate_portion(self, value):
        max_value_to_set = reason = None

        # prevent exceeding employee's pensum additional hours limit
        url_kwargs = self.context['request'].resolver_match.kwargs
        # get filter kwargs from request's URL
        module_filter_kwargs = {
            'schedule__slug': url_kwargs['schedule_slug'],
            'module_code': self.initial_data.get('module')}
        # finding parent module instance
        module = get_object_or_404(Modules, **module_filter_kwargs)
        pensum_filter_kwargs = {
            'schedule__slug': url_kwargs['schedule_slug'],
            'employee__abbreviation': url_kwargs['pensums_employee']}
        # finding parent pensum instance
        pensum = get_object_or_404(Pensum, **pensum_filter_kwargs)
        exam_hours = get_exam_hours(module, self.initial_data.get('type'))
        if module.main_order and module.main_order.students_number > ExamsFactors.min_students_number:
            if pensum.amount_until_over_time_hours_limit < exam_hours * (
                value - (self.instance.portion if self.instance else 0)
            ):
                # flooring decimals is needed as rounding up would exceed limit even more
                max_value_to_set = math.floor(pensum.amount_until_over_time_hours_limit / exam_hours + (
                    self.instance.portion if self.instance else 0) * 1000) / 1000
                reason = "Value exceeds employee's pensum additional hours limit."

        # get sum of all portions for this module's exam
        module = get_object_or_404(Modules, **{'module_code': self.initial_data.get('module')})
        portion_to_set = module.exams_portion_staffed
        if self.instance:
            portion_to_set -= self.instance.portion
        if value + portion_to_set > 1:
            if not max_value_to_set or max_value_to_set > 1 - portion_to_set:
                max_value_to_set = 1 - portion_to_set
                reason = "Sum of all portions for this module's exams would exceed 1."

        if max_value_to_set:
            raise ValidationError(f"Max. value possible: {max_value_to_set}."
                                  f"{' Reason: {}'.format(reason) if reason else ''}")
        return value


class PensumSerializer(NestedHyperlinkedModelSerializer):
    class Meta:
        model = Pensum
        fields = ['url',
                  # employee's data section:
                  'employee_url', 'first_name', 'last_name', 'employee', 'e_mail', 'pensum_group',
                  # basic threshold section:
                  'basic_threshold', 'part_of_job_time', 'basic_threshold_factors_url', 'basic_threshold_factors',
                  'reduction_url', 'reduction', 'calculated_threshold',
                  # contact hours section:
                  'min_for_contact_hours', 'amount_until_contact_hours_min',
                  'pensum_contact_hours',
                  'limit_for_contact_hours', 'amount_until_contact_hours_limit',
                  'limit_for_over_time_hours', 'amount_until_over_time_hours_limit',
                  'plans',
                  # additional hours section:
                  'pensum_additional_hours', 'pensum_additional_hours_not_counted_into_limit',
                  'additional_hours_factors_url', 'additional_hours_factors',
                  'exams_additional_hours_url', 'exams_additional_hours',
                  # hidden
                  'schedule']
        extra_kwargs = {
            'basic_threshold': {'min_value': 0}
        }

    parent_lookup_kwargs = {
        'schedule_slug': 'schedule__slug'
    }
    url = AdvNestedHyperlinkedIdentityField(
        view_name='pensums-detail',
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
    first_name = StringRelatedField(read_only=True, source='employee.first_name')
    last_name = StringRelatedField(read_only=True, source='employee.last_name')
    employee = SlugRelatedField(queryset=Employees.objects.all(), slug_field='abbreviation')
    e_mail = StringRelatedField(read_only=True, source='employee.e_mail')
    pensum_group = StringRelatedField(read_only=True, source='employee.pensum_group')

    part_of_job_time = StringRelatedField(read_only=True, source='employee.part_of_job_time')
    basic_threshold_factors_url = AdvNestedHyperlinkedIdentityField(
        view_name='pensum-factors-list',
        lookup_field=None,
        parent_lookup_kwargs={
            **parent_lookup_kwargs,
            'pensums_employee': 'employee__abbreviation'
        }
    )
    basic_threshold_factors = PensumBasicThresholdFactorSerializer(read_only=True, many=True)
    reduction_url = AdvNestedHyperlinkedIdentityField(
        view_name='pensum-reduction-detail',
        lookup_field=None,
        parent_lookup_kwargs={
            **parent_lookup_kwargs,
            'pensums_employee': 'employee__abbreviation'
        }
    )
    reduction = PensumReductionSerializer(read_only=True)

    plans = EmployeePlansSerializer(many=True, read_only=True, source='employee.plans')

    additional_hours_factors_url = AdvNestedHyperlinkedIdentityField(
        view_name='pensum-additional_hours_factors-list',
        lookup_field=None,
        parent_lookup_kwargs={
            **parent_lookup_kwargs,
            'pensums_employee': 'employee__abbreviation'
        }
    )
    additional_hours_factors = PensumAdditionalHoursFactorsSerializer(many=True, read_only=True)
    exams_additional_hours_url = AdvNestedHyperlinkedIdentityField(
        view_name='pensum-exams_additional_hours-list',
        lookup_field=None,
        parent_lookup_kwargs={
            **parent_lookup_kwargs,
            'pensums_employee': 'employee__abbreviation'
        }
    )
    exams_additional_hours = ExamsAdditionalHoursSerializer(many=True, read_only=True)

    schedule = ParentHiddenRelatedField(
        queryset=Schedules.objects.all(),
        parent_lookup_kwargs={
            'schedule_slug': 'slug'
        },
    )


class PensumListSerializer(PensumSerializer):
    class Meta:
        model = Pensum
        fields = ['url',
                  'employee_url', 'first_name', 'last_name', 'employee', 'pensum_group',
                  'calculated_threshold',
                  'pensum_contact_hours', 'amount_until_contact_hours_min',
                  'pensum_additional_hours', 'amount_until_over_time_hours_limit']
