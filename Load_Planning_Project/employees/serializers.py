from rest_framework.relations import HyperlinkedIdentityField, HyperlinkedRelatedField
from rest_framework.reverse import reverse
from rest_framework.serializers import HyperlinkedModelSerializer, SerializerMethodField
from rest_framework.serializers import ValidationError

from .models import Degrees, Positions, Employees, Modules, Classes


class SerializerLambdaField(SerializerMethodField):
    """
    SerializerLambdaField - Custom Serializer Method Field
    Allows use of lambda function as parameter
    """
    def bind(self, field_name, parent):
        super(SerializerMethodField, self).bind(field_name, parent)

    def to_representation(self, data):
        return self.method_name(data)


class EmployeeShortSerializer(HyperlinkedModelSerializer):
    """
    Employee Short Serializer - simple serializer with url and very basic model fields
    """
    class Meta:
        model = Employees
        fields = ['url', 'first_name', 'last_name', 'abbreviation']
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


class EmployeeSerializer(HyperlinkedModelSerializer):
    """
    Employee Serializer - extended short serializer with additional properties:
    *_repr - string representation of hyperlinked field
    subordinates - nested serializer of employee's subordinates
    modules - hyperlink to nested view of employee's modules
    """
    degree = HyperlinkedRelatedField(
        view_name='degrees-detail',
        queryset=Degrees.objects.order_by('name'),
    )
    degree_repr = SerializerLambdaField(lambda obj: '{}'.format(obj.degree))
    position = HyperlinkedRelatedField(
        view_name='positions-detail',
        queryset=Positions.objects.order_by('name'),
    )
    position_repr = SerializerLambdaField(lambda obj: '{}'.format(obj.position))
    supervisor = HyperlinkedRelatedField(
        view_name='employees-detail',
        queryset=Employees.objects.order_by('abbreviation'),
        allow_null=True,
        lookup_field='abbreviation',
    )
    supervisor_repr = SerializerLambdaField(lambda obj: '{}'.format(obj.supervisor))
    subordinates = EmployeeShortSerializer(read_only=True, many=True)
    modules = HyperlinkedIdentityField(
        view_name='employee-modules-list',
        lookup_field='abbreviation',
        lookup_url_kwarg='employee_abbreviation',
    )

    # custom validator for supervisor field - not allowing setting employee as it's supervisor
    def validate_supervisor(self, data):
        if data:
            # supervisor's sent field is compared to user's url - cannot match!
            if self.initial_data.get('supervisor') == self.context.get('request').build_absolute_uri():
                raise ValidationError("Cannot self reference that field!")
            # fix for uploading csv files
            if self.initial_data.get('abbreviation') == data.abbreviation:
                raise ValidationError("Cannot self reference that field!")
        return data

    # custom validator: 'year of studies' > 0 - DRF mapping PositiveInteger model Field into Integer serializer Field!
    def validate_year_of_studies(self, data):
        if data is None:
            return data
        if data < 0:
            raise ValidationError("Only positive numbers!")
        return data

    class Meta:
        model = Employees
        fields = '__all__'
        extra_kwargs = {
            # url's custom lookup - needs to match lookup set in the view set
            'url': {'lookup_field': 'abbreviation'},
        }


class ModuleClassSerializer(HyperlinkedModelSerializer):
    """
    Module-Class Serializer - simple serializer with url, classes name and hours
    Needs custom url generation because of 'unique_together' Classes' property (two primary keys)
    """
    url = SerializerMethodField('get_two_key_url')

    class Meta:
        model = Classes
        fields = ['url', 'name', 'classes_hours']

    def get_two_key_url(self, data):
        # unique url for classes - need to match path in the urls responsible for classes-detail pattern
        return '{base_url}{module_code}/class/{name}'.format(
            base_url=self.context.get('request').build_absolute_uri(reverse('modules-list')),
            module_code=data.module.module_code,
            name=data.name,
        )


class ClassDetailSerializer(ModuleClassSerializer):
    """
    Class Detail Serializer - extended serializer with additional module's hyperlink, but with no url in fields
    """
    module = HyperlinkedRelatedField(
        view_name='modules-detail',
        queryset=Modules.objects.order_by('module_code'),
        lookup_field='module_code',
    )

    class Meta:
        model = Classes
        fields = ['module', 'name', 'classes_hours']


class ClassFullSerializer(ClassDetailSerializer):
    """
    Class Full Serializer - serializer with all fields
    """
    class Meta:
        model = Classes
        fields = '__all__'


class ModuleSerializer(HyperlinkedModelSerializer):
    """
    Module Serializer - serializer with url, some of the model's fields and additional properties:
    form_of_classes - nested serializer of module's classes
    """
    form_of_classes = ModuleClassSerializer(read_only=True, many=True)

    class Meta:
        model = Modules
        fields = ['url', 'module_code', 'name', 'examination', 'form_of_classes']
        extra_kwargs = {
            # url's custom lookup - needs to match lookup set in the view set
            'url': {'lookup_field': 'module_code'},
        }
