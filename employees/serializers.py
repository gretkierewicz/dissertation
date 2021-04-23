from rest_framework.relations import HyperlinkedIdentityField, SlugRelatedField
from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer

from utils.relations import AdvNestedHyperlinkedIdentityField
from .models import Degrees, Employees, Positions


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


class SupervisorField(SlugRelatedField):
    """
    Supervisor Field to filter instance of employee from basic queryset
    """

    def get_queryset(self):
        return self.queryset.exclude(pk=self.root.instance.pk) if self.root.instance else self.queryset


class EmployeeSerializer(ModelSerializer):
    """
    Employee Serializer - Extended Employee Serializer with additional urls and nested serializers
    """

    class Meta:
        model = Employees
        fields = ['url', 'first_name', 'last_name', 'abbreviation', 'e_mail', 'degree', 'position', 'pensum_group',
                  'part_of_job_time', 'supervisor_url', 'supervisor', 'subordinates',
                  'year_of_studies', 'has_scholarship', 'is_procedure_for_a_doctoral_degree_approved']
        extra_kwargs = {
            'year_of_studies': {'min_value': 0},
            'part_of_job_time': {'min_value': 0, 'max_value': 1}
        }

    url = HyperlinkedIdentityField(view_name='employees-detail', lookup_field='abbreviation')

    degree = SlugRelatedField(slug_field='name', queryset=Degrees.objects.all())
    position = SlugRelatedField(slug_field='name', queryset=Positions.objects.all())
    supervisor = SupervisorField(slug_field='abbreviation', queryset=Employees.objects.all(), allow_null=True)

    supervisor_url = AdvNestedHyperlinkedIdentityField(
        view_name='employees-detail',
        lookup_field=None,
        parent_lookup_kwargs={
            'abbreviation': 'supervisor__abbreviation'
        }
    )
    subordinates = EmployeeListSerializer(read_only=True, many=True)
