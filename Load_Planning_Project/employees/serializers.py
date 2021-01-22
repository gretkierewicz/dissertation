from rest_framework.relations import HyperlinkedIdentityField, SlugRelatedField
from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer
from rest_framework.serializers import ValidationError

from .models import Degrees, Positions, Employees, Pensum
from modules.serializers import SupervisedModuleSerializer, EmployeePlanModulesSerializer
from utils.constants import NA


class EmployeeListSerializer(HyperlinkedModelSerializer):
    """
    Employee Short Serializer - simple serializer with url and very basic model fields
    """
    class Meta:
        model = Employees
        fields = ['url',
                  'first_name', 'last_name', 'abbreviation', 'e_mail']
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
        fields = ['url', 'name', 'value', 'limit', 'degrees', 'positions', 'year_of_studies', 'year_condition',
                  'is_procedure_for_a_doctoral_degree_approved', 'has_scholarship']
        extra_kwargs = {
            'year_condition': {'allow_null': False, 'initial': 'N/A'},
            'is_procedure_for_a_doctoral_degree_approved': {'allow_null': False, 'initial': 'N/A'},
            'has_scholarship': {'allow_null': False, 'initial': 'N/A'},
        }

    url = HyperlinkedIdentityField(view_name='pensum-detail')

    degrees = SlugRelatedField(slug_field='name', queryset=Degrees.objects.all(), many=True)
    positions = SlugRelatedField(slug_field='name', queryset=Positions.objects.all(), many=True)

    def validate(self, attrs):
        # don't allow same match-ups of field's values
        query = Pensum.objects.exclude(pk=self.instance.pk) if self.instance else Pensum.objects.all()
        query = query.filter(
            degrees__in=attrs.get('degrees') or (self.instance.degrees.all() if self.instance else None),
            positions__in=attrs.get('positions') or (self.instance.positions.all() if self.instance else None)
        )
        year_of_studies = attrs.get('year_of_studies') or (self.instance.year_of_studies if self.instance else None)
        year_condition = attrs.get('year_condition') or (self.instance.year_condition if self.instance else None)
        if year_of_studies and year_condition and year_condition != NA:
            # TODO: not perfect solution - different pensum records can cover same year range
            query = query.filter(year_of_studies=year_of_studies, year_condition=year_condition)

        is_procedure_for_a_doctoral_degree_approved = attrs.get('is_procedure_for_a_doctoral_degree_approved') or (
            self.instance.is_procedure_for_a_doctoral_degree_approved if self.instance else None)
        if is_procedure_for_a_doctoral_degree_approved and is_procedure_for_a_doctoral_degree_approved != NA:
            query = query.filter(
                is_procedure_for_a_doctoral_degree_approved=is_procedure_for_a_doctoral_degree_approved)

        has_scholarship = attrs.get('has_scholarship') or (self.instance.has_scholarship if self.instance else None)
        if has_scholarship and has_scholarship != NA:
            query = query.filter(has_scholarship=has_scholarship)
        if len(query) != 0:
            # list all pensum found (rip off square parenthesis)
            raise ValidationError(f"Given combination exists in another pensum record(s): "
                                  f"{str([pensum.name for pensum in query.distinct()])[1:-1]}")
        return attrs

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
        fields = ['url', 'first_name', 'last_name', 'abbreviation', 'e_mail', 'degree', 'position',
                  'pensum_name', 'pensum_value', 'is_pensum_value_reached', 'pensum_limit', 'is_pensum_limit_reached',
                  'plan_hours_sum', 'plan_modules_url', 'plan_modules',
                  'supervised_modules_url', 'supervised_modules', 'supervisor_url', 'supervisor', 'subordinates',
                  'year_of_studies', 'has_scholarship', 'is_procedure_for_a_doctoral_degree_approved']
        extra_kwargs = {
            'year_of_studies': {'min_value': 0}
        }

    url = HyperlinkedIdentityField(view_name='employees-detail', lookup_field='abbreviation')

    degree = SlugRelatedField(slug_field='name', queryset=Degrees.objects.all())
    position = SlugRelatedField(slug_field='name', queryset=Positions.objects.all())
    supervisor = SlugRelatedField(slug_field='abbreviation', queryset=Employees.objects.all(), allow_null=True)

    plan_modules_url = HyperlinkedIdentityField(
        view_name='employee-plans-list', lookup_field='abbreviation', lookup_url_kwarg='employee_abbreviation')
    # queryset given by model's property is transferred to the proper serializer
    plan_modules = EmployeePlanModulesSerializer(read_only=True, many=True)

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
