import re

from rest_framework.fields import HiddenField
from rest_framework.relations import HyperlinkedIdentityField, HyperlinkedRelatedField
from rest_framework.serializers import HyperlinkedModelSerializer, SerializerMethodField
from rest_framework.serializers import ValidationError
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer

from .models import Degrees, Positions, Employees, Modules, Classes


class ParentFromURLHiddenField(HiddenField):
    """
    ParentFromURLHiddenField - Hidden Field that doesn't take value from user, but return searched object
    It will create filter kwargs with help of provided dictionary (matches) and context's request path.
    Be sure that URL is composed by */url_lookup/slug/* pairs.
    If you give more matches, all will be considered as filter kwargs.
    params:
    queryset - object to filter by
    matches - dictionary of url lookups (keys) and field's names (values)
    returns:
     - model's instance filtered from the queryset (first occurrence - slug should be unique by default!)
    """
    def __init__(self, queryset, matches, **kwargs):
        self.queryset = queryset
        self.matches = matches
        kwargs['write_only'] = True
        kwargs['default'] = None
        super().__init__(**kwargs)

    def get_value(self, dictionary):
        # change data forwarded to the to_internal_value()
        filter_kwargs = {}
        for lookup, field in self.matches.items():
            filter_kwargs[field] = re.search(
                r'{lookup}/(?P<slug>[\w\-_]+)/'.format(lookup=lookup),
                self.context['request'].path
            ).group('slug')
        return self.queryset.filter(**filter_kwargs).first()

    def to_internal_value(self, data):
        # return model's instance, no conversion needed
        return data


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


class ClassSerializer(NestedHyperlinkedModelSerializer):
    """
    Class Serializer - only for nesting in the Module Serializer
    """
    parent_lookup_kwargs = {
        'module_module_code': 'module__module_code',
    }
    # New type of Field made - module should be never provided by the user!
    # Requested URL should point one parent object - in this case module's code
    module = ParentFromURLHiddenField(
        # queryset that will be filtered with {module_code: code_slug} filter
        queryset=Modules.objects.all(),
        # it should match object by the request's URL: */modules/code_slug/*
        matches={'modules': 'module_code'},
    )

    class Meta:
        model = Classes
        fields = ['url', 'name', 'module', 'classes_hours']
        extra_kwargs = {
            # url's custom lookup - needs to match lookup set in the view set
            'url': {'lookup_field': 'name'},
        }


class ModuleSerializer(HyperlinkedModelSerializer):
    """
    Module Serializer - serializer with url, some of the model's fields and additional properties:
    form_of_classes - nested serializer of module's classes
    """
    classes = HyperlinkedIdentityField(
        view_name='classes-list',
        lookup_field='module_code',
        lookup_url_kwarg='module_module_code',
    )
    form_of_classes = ClassSerializer(read_only=True, many=True)
    supervisor = HyperlinkedRelatedField(
        view_name='employees-detail',
        queryset=Employees.objects.order_by('abbreviation'),
        allow_null=True,
        lookup_field='abbreviation',
    )

    class Meta:
        model = Modules
        fields = ['url', 'module_code', 'name', 'examination', 'classes', 'form_of_classes', 'supervisor']
        extra_kwargs = {
            # url's custom lookup - needs to match lookup set in the view set
            'url': {'lookup_field': 'module_code'},
        }
