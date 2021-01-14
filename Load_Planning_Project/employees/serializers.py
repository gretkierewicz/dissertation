from rest_framework.relations import HyperlinkedIdentityField
from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer
from rest_framework.serializers import ValidationError
from rest_framework_nested.relations import NestedHyperlinkedIdentityField
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer

from utils.serializers import ParentFromURLHiddenField, SerializerLambdaField
from utils.validators import validate_if_positive

from .models import Degrees, Positions, Employees, Modules, Classes, Pensum, Plans


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


class PlanSerializer(NestedHyperlinkedModelSerializer):
    class Meta:
        model = Plans
        fields = ['url',
                  'employee', 'employee_repr', 'plan_hours',
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

    employee_repr = SerializerLambdaField(lambda obj: '{}'.format(obj.employee))

    # hidden classes field - pointing parent's object
    classes = ParentFromURLHiddenField(
        queryset=Classes.objects.all(),
        matches={
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
        fields = ['url',
                  'name', 'classes_hours', 'plan_url', 'plan',
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
        matches={'module_module_code': 'module_code'},
    )

    # url of plan: parent's lookup_field (ClassesView); lookup_url_kwarg - lookup from URL that points lookup_field;
    # parent_lookup_kwargs - URL lookup and queryset key (parent_lookup_kwargs of this serializer)
    plan_url = NestedHyperlinkedIdentityField(
        view_name='plans-list',
        lookup_field='name',
        lookup_url_kwarg='class_name',
        parent_lookup_kwargs={
            'module_module_code': 'module__module_code',
        },
    )
    # needs parent_lookup_kwargs configured in nested serializer!
    plan = PlanSerializer(read_only=True, many=True)

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
                  'supervisor', 'supervisor_repr',
                  'classes_url', 'classes']
        extra_kwargs = {
            # url's custom lookup - needs to match lookup set in the view set
            'url': {'lookup_field': 'module_code'},
            'supervisor': {'lookup_field': 'abbreviation', 'allow_null': True}
        }
    parent_lookup_kwargs = {
        'employee_abbreviation': 'supervisor__abbreviation',
    }

    supervisor_repr = SerializerLambdaField(lambda obj: '{}'.format(obj.supervisor))

    classes_url = HyperlinkedIdentityField(
        view_name='classes-list',
        lookup_field='module_code',
        lookup_url_kwarg='module_module_code',
    )
    # needs parent_lookup_kwargs configured in nested serializer!
    classes = ClassSerializer(read_only=True, many=True)


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
                  'subordinates', 'modules_url', 'modules',
                  'year_of_studies', 'has_scholarship', 'is_procedure_for_a_doctoral_degree_approved']
        extra_kwargs = {
            # url's custom lookup - needs to matches lookup set in the view set
            'url': {'lookup_field': 'abbreviation'},
            'degree': {},
            'supervisor': {'lookup_field': 'abbreviation', 'allow_null': True}
        }

    degree_repr = SerializerLambdaField(lambda obj: '{}'.format(obj.degree))
    position_repr = SerializerLambdaField(lambda obj: '{}'.format(obj.position))
    supervisor_repr = SerializerLambdaField(lambda obj: '{}'.format(obj.supervisor))

    subordinates = EmployeeShortSerializer(read_only=True, many=True)

    modules_url = HyperlinkedIdentityField(
        view_name='employee-modules-list',
        lookup_field='abbreviation',
        lookup_url_kwarg='employee_abbreviation',
    )
    modules = ModuleSerializer(read_only=True, many=True)

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
