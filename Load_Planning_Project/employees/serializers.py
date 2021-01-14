import re

from rest_framework.fields import HiddenField
from rest_framework.relations import HyperlinkedIdentityField, HyperlinkedRelatedField
from rest_framework.serializers import HyperlinkedModelSerializer, SerializerMethodField, ModelSerializer
from rest_framework.serializers import ValidationError
from rest_framework_nested.relations import NestedHyperlinkedIdentityField
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer

from .models import Degrees, Positions, Employees, Modules, Classes, Pensum, Plans


def validate_if_positive(value):
    if value is None:
        return value
    if value < 0:
        raise ValidationError("Value must be positive.")
    return value


class ParentFromURLHiddenField(HiddenField):
    """
    ParentFromURLHiddenField - Hidden Field that doesn't take value from user, but return searched object
    It will create filter kwargs with help of provided dictionary (matches) and resolved URL's matches.
    Be sure that parent lookup kwarg's name matches the one configured with serializer and view.
    If you give more matches, all will be considered as filter kwargs.
    params:
    queryset - object to filter by
    matches - dictionary of parent's lookup kwarg's name (keys) and field's names (values)
    returns:
     - model's instance filtered from the queryset (first occurrence - slug should be unique by default!)
    """
    def __init__(self, queryset, match, **kwargs):
        self.queryset = queryset
        self.match = match
        kwargs['write_only'] = True
        kwargs['default'] = None
        super().__init__(**kwargs)

    def get_value(self, dictionary):
        # change data forwarded to the to_internal_value()
        filter_kwargs = {}
        for key, value in self.match.items():
            # getting slug from URL resolver - needs to match parent_lookup_kwarg's name!
            filter_kwargs[value] = self.context.get('request').resolver_match.kwargs[key]
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
                  'pensum', 'limit',
                  'degrees', 'positions']

    url = HyperlinkedIdentityField(view_name='pensum-detail', read_only=True)

    def to_representation(self, instance):
        # changes output representation from primary keys to more readable names
        ret = super().to_representation(instance)
        tmp = []
        for pk in ret['degrees']:
            tmp.append(Degrees.objects.get(pk=pk).name)
        ret['degrees'] = tmp
        tmp = []
        for pk in ret['positions']:
            tmp.append(Positions.objects.get(pk=pk).name)
        ret['positions'] = tmp
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
                  'degree_repr', 'degree',
                  'position_repr', 'position',
                  'supervisor_repr', 'supervisor',
                  'subordinates', 'modules',
                  'year_of_studies', 'has_scholarship', 'is_procedure_for_a_doctoral_degree_approved']
        extra_kwargs = {
            # url's custom lookup - needs to match lookup set in the view set
            'url': {'lookup_field': 'abbreviation'},
            'supervisor': {'lookup_field': 'abbreviation', 'allow_null': True}
        }

    degree_repr = SerializerLambdaField(lambda obj: '{}'.format(obj.degree))
    position_repr = SerializerLambdaField(lambda obj: '{}'.format(obj.position))
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
        return validate_if_positive(data)


class PlanSerializer(NestedHyperlinkedModelSerializer):
    class Meta:
        model = Plans
        fields = ['url',
                  'employee', 'plan_hours',
                  # hidden fields:
                  'classes']
        extra_kwargs = {
            # url's custom lookup - needs to match lookup set in the view set
            'url': {'lookup_field': 'employee'},
            'employee': {'lookup_field': 'abbreviation'},
        }
    # for nesting serializer - dict of URL lookups and queryset kwarg keys
    parent_lookup_kwargs = {
        'module_module_code': 'classes__module__module_code',
        'class_name': 'classes__name',
    }
    # hidden classes field - pointing parent's object
    classes = ParentFromURLHiddenField(
        queryset=Classes.objects.all(),
        match={
            'module_module_code': 'module__module_code',
            'class_name': 'name'
        }
    )


class ClassSerializer(NestedHyperlinkedModelSerializer):
    """
    Class Serializer - only for nesting in the Module Serializer
    """
    class Meta:
        model = Classes
        fields = ['url', 'plans_url',
                  'name', 'classes_hours', 'plans',
                  # hidden fields:
                  'module']
        extra_kwargs = {
            # url's custom lookup - needs to match lookup set in the view set
            'url': {'lookup_field': 'name'},
        }
    # for nesting serializer - dict of URL lookups and queryset kwarg keys
    parent_lookup_kwargs = {
        'module_module_code': 'module__module_code',
    }
    # New type of Field made - module should be never provided by the user!
    # Requested URL should point one parent object - in this case module's code
    module = ParentFromURLHiddenField(
        # queryset that will be filtered
        queryset=Modules.objects.all(),
        # key is a parent_lookup_kwarg, value - a field to filter by
        match={'module_module_code': 'module_code'},
    )
    # url of plan: parent's lookup_field (ClassesView); lookup_url_kwarg - lookup from URL that points lookup_field;
    # parent_lookup_kwargs - URL lookup and queryset key (parent_lookup_kwargs of this serializer)
    plans_url = NestedHyperlinkedIdentityField(
        view_name='plans-list',
        lookup_field='name',
        lookup_url_kwarg='class_name',
        parent_lookup_kwargs={
            'module_module_code': 'module__module_code',
        },
    )
    plans = PlanSerializer(read_only=True, many=True)

    # mapping PositiveInteger model Field into Integer serializer Field issue
    def validate_classes_hours(self, data):
        return validate_if_positive(data)


class ModuleSerializer(HyperlinkedModelSerializer):
    """
    Module Serializer - serializer with url, some of the model's fields and additional properties:
    form_of_classes - nested serializer of module's classes
    """
    class Meta:
        model = Modules
        fields = ['url',
                  'module_code', 'name', 'examination',
                  'classes', 'form_of_classes',
                  'supervisor']
        extra_kwargs = {
            # url's custom lookup - needs to match lookup set in the view set
            'url': {'lookup_field': 'module_code'},
            'supervisor': {'lookup_field': 'abbreviation', 'allow_null': True}
        }

    classes = HyperlinkedIdentityField(
        view_name='classes-list',
        lookup_field='module_code',
        lookup_url_kwarg='module_module_code',
    )
    form_of_classes = ClassSerializer(read_only=True, many=True)
