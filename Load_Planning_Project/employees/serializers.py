from rest_framework.relations import HyperlinkedIdentityField
from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer
from rest_framework.serializers import ValidationError

from utils.serializers import conv_pk_to_str

from .models import Degrees, Positions, Employees, Pensum
from modules.serializers import SupervisedModuleSerializer, EmployeePlanSerializer


class EmployeeListSerializer(HyperlinkedModelSerializer):
    """
    Employee Short Serializer - simple serializer with url and very basic model fields
    """
    class Meta:
        model = Employees
        fields = ['url',
                  'first_name', 'last_name', 'abbreviation']
        extra_kwargs = {
            'url': {'lookup_field': 'abbreviation'},
        }


class DegreeSerializer(HyperlinkedModelSerializer):
    """
    Degree Serializer - serializer with url, model's field and additional employee list
    """
    class Meta:
        model = Degrees
        fields = ['url', 'name', 'employees']

    employees = EmployeeListSerializer(read_only=True, many=True)


class PositionSerializer(HyperlinkedModelSerializer):
    """
    Position Serializer - serializer with url, model's field and additional employee list
    """
    class Meta:
        model = Positions
        fields = ['url', 'name', 'employees']

    employees = EmployeeListSerializer(read_only=True, many=True)


class PensumSerializer(ModelSerializer):
    """
    Pensum Serializer - for covering min and max number of hours for each employee by his/her degree and position
    """
    class Meta:
        model = Pensum
        fields = ['url', 'value', 'limit', 'degrees', 'positions']
        extra_kwargs = {
            'degrees': {'queryset': Degrees.objects.all()},
            'positions': {'queryset': Positions.objects.all()},
        }

    url = HyperlinkedIdentityField(view_name='pensum-detail')

    def to_representation(self, instance):
        # changes output representation from primary keys to more readable strings
        ret = super().to_representation(instance)
        return conv_pk_to_str(obj=ret, key_to_model_dict={
            'degrees': Degrees, 'positions': Positions
        }) if self.context.get('request').method == 'GET' else ret

    def validate(self, attrs):
        # don't allow double match-ups of degree and position
        # TODO: implement fix for PATCH method (now it fails in cases of missing 'degrees' or 'positions' lists
        # object should be taken from instance or URL kwarg, not from attrs!
        # self.context['request'].resolver_match.kwargs
        query = Pensum.objects.filter(degrees__in=attrs.get('degrees'), positions__in=attrs.get('positions')).distinct()
        if len(query) == 0 or (len(query) == 1 and self.instance in query):
            return attrs
        raise ValidationError('Given combination of degree and position exists in another pensum record(s).')

    def validate_limit(self, data):
        # validation for proper setting of pensum's limit (cannot be lower than given value)
        # TODO: validation fails for PATCH method
        init_value = int(self.initial_data['value'] or 0)
        init_limit = int(self.initial_data['limit'] or 0)
        if not self.instance:
            if init_limit <= init_value:
                raise ValidationError(f"Limit ({init_limit}) cannot be lower or equal than value ({init_value}).")
        # 0 if no limit provided (empty limit field)
        # instance's 'value' field taken into account only when 'value' field value missing or equal 0
        elif (data or 0) <= (init_value or self.instance.value):
            raise ValidationError(
                f"Limit ({data or 0}) cannot be lower or equal than value ({init_value or self.instance.value}).")
        return data


class EmployeeSerializer(ModelSerializer):
    """
    Employee Serializer - Extended Employee Serializer with additional urls and nested serializers
    """
    class Meta:
        model = Employees
        fields = ['url', 'first_name', 'last_name', 'abbreviation', 'e_mail',
                  'degree', 'position', 'pensum_value', 'pensum_limit',
                  'plan_hours_sum', 'plan_modules_url', 'plan_modules',
                  'supervised_modules_url', 'supervised_modules', 'supervisor_url', 'supervisor', 'subordinates',
                  'year_of_studies', 'has_scholarship', 'is_procedure_for_a_doctoral_degree_approved']
        extra_kwargs = {
            'degree': {'queryset': Degrees.objects.all()},
            'position': {'queryset': Positions.objects.all()},
            'supervisor': {'queryset': Employees.objects.all()},
            'year_of_studies': {'min_value': 0}
        }

    url = HyperlinkedIdentityField(view_name='employees-detail', lookup_field='abbreviation')

    plan_modules_url = HyperlinkedIdentityField(
        view_name='employee-plans-list', lookup_field='abbreviation', lookup_url_kwarg='employee_abbreviation')
    # queryset given by model's property is transferred to the proper serializer
    plan_modules = EmployeePlanSerializer(read_only=True, many=True)

    supervised_modules_url = HyperlinkedIdentityField(
        view_name='employee-modules-list', lookup_field='abbreviation', lookup_url_kwarg='employee_abbreviation')
    supervised_modules = SupervisedModuleSerializer(read_only=True, many=True)

    supervisor_url = HyperlinkedIdentityField(
        view_name='employees-detail', lookup_field='supervisor', lookup_url_kwarg='abbreviation')
    subordinates = EmployeeListSerializer(read_only=True, many=True)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        return conv_pk_to_str(obj=ret, key_to_model_dict={
            'degree': Degrees, 'position': Positions, 'supervisor': Employees
        }) if self.context.get('request').method == 'GET' else ret

    # custom validator for supervisor field - not allowing setting employee as it's supervisor
    def validate_supervisor(self, data):
        if data:
            # supervisor's sent field is compared to user's url - cannot matches!
            if self.initial_data.get('supervisor') == self.context.get('request').build_absolute_uri():
                raise ValidationError("Cannot self reference that field!")
            # fix for uploading csv files
            if self.initial_data.get('abbreviation') == data.abbreviation:
                raise ValidationError("Cannot self reference that field!")
        return data
