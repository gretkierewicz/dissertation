from rest_framework.relations import HyperlinkedIdentityField
from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer
from rest_framework.serializers import ValidationError

from utils.serializers import conv_pk_to_str
from utils.validators import validate_if_positive

from .models import Degrees, Positions, Employees, Pensum


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
        fields = ['url', 'pensum', 'limit', 'degrees', 'positions']

    url = HyperlinkedIdentityField(view_name='pensum-detail')

    def to_representation(self, instance):
        # changes output representation from primary keys to more readable strings
        ret = super().to_representation(instance)
        return conv_pk_to_str(obj=ret, key_to_model_dict={
            'degrees': Degrees, 'positions': Positions
        }) if self.context.get('request').method == 'GET' else ret


class EmployeeSerializer(ModelSerializer):
    """
    Employee Serializer - extended short serializer with additional properties:
    *_repr - string representation of hyperlinked field
    subordinates - nested serializer of employee's subordinates
    modules - hyperlink to nested view of employee's modules
    """
    class Meta:
        model = Employees
        fields = ['url', 'first_name', 'last_name', 'abbreviation', 'e_mail',
                  'degree', 'position', 'supervisor', 'supervisor_url', 'subordinates', 'modules_url',# 'modules',
                  'year_of_studies', 'has_scholarship', 'is_procedure_for_a_doctoral_degree_approved']

    url = HyperlinkedIdentityField(view_name='employees-detail', lookup_field='abbreviation')
    supervisor_url = HyperlinkedIdentityField(
        view_name='employees-detail', lookup_field='supervisor', lookup_url_kwarg='abbreviation')
    modules_url = HyperlinkedIdentityField(
        view_name='employee-modules-list', lookup_field='abbreviation', lookup_url_kwarg='employee_abbreviation')

    subordinates = EmployeeListSerializer(read_only=True, many=True)

    # TODO: needs custom serializer!
    #modules = ModuleSerializer(read_only=True, many=True)

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

    # custom validator: 'year of studies' > 0 - DRF mapping PositiveInteger model Field into Integer serializer Field!
    def validate_year_of_studies(self, data):
        return validate_if_positive(data)

