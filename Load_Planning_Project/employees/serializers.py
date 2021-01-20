from rest_framework.relations import HyperlinkedIdentityField, SlugRelatedField
from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer
from rest_framework.serializers import ValidationError

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

    url = HyperlinkedIdentityField(view_name='pensum-detail')

    degrees = SlugRelatedField(slug_field='name', queryset=Degrees.objects.all(), many=True)
    positions = SlugRelatedField(slug_field='name', queryset=Positions.objects.all(), many=True)

    def validate(self, attrs):
        # don't allow double match-ups of degree and position
        degrees = attrs.get('degrees') or (self.instance.degrees.all() if self.instance else None)
        positions = attrs.get('positions') or (self.instance.positions.all() if self.instance else None)
        query = Pensum.objects.filter(degrees__in=degrees, positions__in=positions).distinct()
        if len(query) == 0 or (len(query) == 1 and self.instance in query):
            return attrs
        raise ValidationError('Given combination of degree and position exists in another pensum record(s).')

    def validate_limit(self, data):
        # validation for proper setting of pensum's limit
        value = int(self.initial_data.get('value') or (self.instance.value if self.instance else 0))
        limit = int(data or (self.instance.limit if self.instance else 0))
        if limit <= value:
            raise ValidationError(f"Limit ({limit}) cannot be lower or equal to value ({value}).")
        return data

    def validate_value(self, data):
        # validation for proper setting of pensum's value
        value = int(data or (self.instance.value if self.instance else 0))
        limit = int(self.initial_data.get('limit') or (self.instance.limit if self.instance else 0))
        if limit <= value:
            raise ValidationError(f"Limit ({limit}) cannot be lower or equal to value ({value}).")
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
            'year_of_studies': {'min_value': 0}
        }

    url = HyperlinkedIdentityField(view_name='employees-detail', lookup_field='abbreviation')

    degree = SlugRelatedField(slug_field='name', queryset=Degrees.objects.all())
    position = SlugRelatedField(slug_field='name', queryset=Positions.objects.all())
    supervisor = SlugRelatedField(slug_field='abbreviation', queryset=Employees.objects.all())

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
