from rest_framework.relations import HyperlinkedIdentityField, HyperlinkedRelatedField
from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer
from rest_framework.serializers import ValidationError

from utils.serializers import SerializerLambdaField
from utils.validators import validate_if_positive

from .models import Degrees, Positions, Employees, Pensum


class EmployeeShortSerializer(HyperlinkedModelSerializer):
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


class DegreeShortSerializer(HyperlinkedModelSerializer):
    """
    Degree Short Serializer - simple serializer with url and model's fields
    """
    class Meta:
        model = Degrees
        fields = '__all__'


class DegreeSerializer(DegreeShortSerializer):
    """
    Degree Serializer - extended short serializer with nested employees short serializer
    """
    employees = EmployeeShortSerializer(read_only=True, many=True)


class PositionShortSerializer(HyperlinkedModelSerializer):
    """
    Position Short Serializer - simple serializer with url and model's fields
    """
    class Meta:
        model = Positions
        fields = '__all__'


class PositionSerializer(PositionShortSerializer):
    """
    Position Serializer - extended short serializer with nested employees short serializer
    """
    employees = EmployeeShortSerializer(read_only=True, many=True)


class PensumSerializer(ModelSerializer):
    """
    Pensum Serializer - for covering min and max number of hours for each employee by his/her degree and position
    """
    class Meta:
        model = Pensum
        fields = ['url',
                  'pensum', 'limit', 'degrees', 'positions']

    url = HyperlinkedIdentityField(view_name='pensum-detail', read_only=True)

    def to_representation(self, instance):
        # changes output representation from primary keys to more readable: names
        ret = super().to_representation(instance)
        ret['degrees'] = [Degrees.objects.get(pk=pk).name for pk in ret['degrees']]
        ret['positions'] = [Positions.objects.get(pk=pk).name for pk in ret['positions']]
        return ret


class EmployeeSerializer(HyperlinkedModelSerializer):
    """
    Employee Serializer - extended short serializer with additional properties:
    *_repr - string representation of hyperlinked field
    subordinates - nested serializer of employee's subordinates
    modules - hyperlink to nested view of employee's modules
    """
    class Meta:
        model = Employees
        fields = ['url',
                  'first_name', 'last_name', 'abbreviation', 'e_mail',
                  'degree', 'degree_repr', 'position_repr', 'position', 'supervisor_repr', 'supervisor',
                  'subordinates', 'modules_url',# 'modules',
                  'year_of_studies', 'has_scholarship', 'is_procedure_for_a_doctoral_degree_approved']
        extra_kwargs = {
            # url's custom lookup - needs to matches lookup set in the view set
            'url': {'lookup_field': 'abbreviation'},
            'supervisor': {'lookup_field': 'abbreviation', 'allow_null': True}
        }

    # ensures that in forms, there cannot be None option
    degree = HyperlinkedRelatedField(
        view_name='degrees-detail',
        queryset=Degrees.objects.order_by('name'),
    )
    degree_repr = SerializerLambdaField(lambda obj: '{}'.format(obj.degree))
    # ensures that in forms, there cannot be None option
    position = HyperlinkedRelatedField(
        view_name='positions-detail',
        queryset=Positions.objects.order_by('name'),
    )
    position_repr = SerializerLambdaField(lambda obj: '{}'.format(obj.position))
    supervisor_repr = SerializerLambdaField(lambda obj: '{}'.format(obj.supervisor))

    subordinates = EmployeeShortSerializer(read_only=True, many=True)

    modules_url = HyperlinkedIdentityField(
        view_name='employee-modules-list',
        lookup_field='abbreviation',
        lookup_url_kwarg='employee_abbreviation',
    )
    # TODO: needs custom serializer!
    #modules = ModuleSerializer(read_only=True, many=True)

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

    # custom validator: 'year of studies' > 0 - DRF mapping PositiveInteger model Field into Integer serializer Field!
    def validate_year_of_studies(self, data):
        return validate_if_positive(data)
