from rest_framework.relations import HyperlinkedIdentityField, SlugRelatedField
from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer
from rest_framework.serializers import ValidationError

from .models import Degrees, Positions, Employees


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


class EmployeeSerializer(ModelSerializer):
    """
    Employee Serializer - Extended Employee Serializer with additional urls and nested serializers
    """
    class Meta:
        model = Employees
        fields = ['url', 'first_name', 'last_name', 'abbreviation', 'e_mail', 'degree', 'position',
                  'supervisor_url', 'supervisor', 'subordinates',
                  'year_of_studies', 'has_scholarship', 'is_procedure_for_a_doctoral_degree_approved']
        extra_kwargs = {
            'year_of_studies': {'min_value': 0}
        }

    url = HyperlinkedIdentityField(view_name='employees-detail', lookup_field='abbreviation')

    degree = SlugRelatedField(slug_field='name', queryset=Degrees.objects.all())
    position = SlugRelatedField(slug_field='name', queryset=Positions.objects.all())
    supervisor = SlugRelatedField(slug_field='abbreviation', queryset=Employees.objects.all(), allow_null=True)

    supervisor_url = HyperlinkedIdentityField(
        view_name='employees-detail', lookup_field='supervisor', lookup_url_kwarg='abbreviation')
    subordinates = EmployeeListSerializer(read_only=True, many=True)

    # custom validator for supervisor field - not allowing setting employee as it's supervisor
    def validate_supervisor(self, data):
        abbreviation = self.initial_data.get('abbreviation') or (self.instance.abbreviation if self.instance else None)
        if data and abbreviation and abbreviation == data.abbreviation:
            raise ValidationError("Employee cannot be it's own Supervisor")
        return data
