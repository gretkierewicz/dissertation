from rest_framework.relations import HyperlinkedIdentityField, SlugRelatedField
from rest_framework.serializers import HyperlinkedModelSerializer
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer

from orders.serializers import ClassesOrderSerializer
from utils.serializers import GetParentHiddenField

from .models import Modules, Classes
from employees.models import Employees


class ClassSerializer(NestedHyperlinkedModelSerializer):
    """
    Class Serializer - only for nesting in the Module Serializer
    """
    class Meta:
        model = Classes
        fields = ['url', 'name', 'classes_hours', 'students_limit_per_group', 'order',
                  # hidden fields:
                  'module']
        extra_kwargs = {
            # url's custom lookup - needs to match lookup set in the view set
            'url': {'lookup_field': 'name'},
            'classes_hours': {'min_value': 0},
            'students_limit_per_group': {'min_value': 0},
        }
    # for nesting serializer - dict of URL lookups and queryset kwarg keys
    parent_lookup_kwargs = {
        'module_module_code': 'module__module_code',
    }

    order = ClassesOrderSerializer(read_only=True)

    # New type of Field made - module should be never provided by the user!
    # Requested URL should point one parent object - in this case module's code
    module = GetParentHiddenField(
        # queryset that will be filtered
        queryset=Modules.objects.all(),
        # key is a parent_lookup_kwarg, value - a field to filter by
        parent_lookup_kwargs={'module_module_code': 'module_code'},
        # in case of no valid URL (i.e. JSON data upload) look for parent passed in create/update methods
        parent_lookup='module',
    )


class ModuleSerializer(HyperlinkedModelSerializer):
    """
    Module Serializer - serializer with url, some of the model's fields and additional properties:
    form_of_classes - nested serializer of module's classes
    """
    class Meta:
        model = Modules
        fields = ['url',
                  'module_code', 'name',
                  'supervisor', 'supervisor_url', 'examination',
                  'classes_url', 'classes']
        extra_kwargs = {
            # url's custom lookup - needs to match lookup set in the view set
            'url': {'lookup_field': 'module_code'},
        }

    supervisor = SlugRelatedField(slug_field='abbreviation', queryset=Employees.objects.all(), allow_null=True)
    supervisor_url = HyperlinkedIdentityField(
        view_name='employees-detail',
        lookup_field='supervisor',
        lookup_url_kwarg='abbreviation'
    )

    classes_url = HyperlinkedIdentityField(
        view_name='classes-list',
        lookup_field='module_code',
        lookup_url_kwarg='module_module_code',
    )
    # needs parent_lookup_kwargs configured in nested serializer!
    classes = ClassSerializer(read_only=True, many=True)

    # overwrite for handling nested classes (this will not delete missing classes in data)
    def create(self, validated_data):
        module = super().create(validated_data)
        if self.initial_data.get('classes'):
            for classes_data in self.initial_data.get('classes'):
                # additionally passing module instance for classes hidden field
                classes_data['module'] = module
                serializer = ClassSerializer(instance=module.classes.filter(name=classes_data.get('name')).first(),
                                             data=classes_data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    # TODO: need to pass this somehow to user:
                    print(serializer.errors)
        return module

    # overwrite for handling nested classes (this will not delete missing classes in data)
    def update(self, instance, validated_data):
        module = super().update(instance, validated_data)
        if self.initial_data.get('classes'):
            for classes_data in self.initial_data.get('classes'):
                # additionally passing module instance for classes hidden field
                classes_data['module'] = module
                serializer = ClassSerializer(instance=module.classes.filter(name=classes_data.get('name')).first(),
                                             data=classes_data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    # TODO: need to pass this somehow to user:
                    print(serializer.errors)
        return module


class ModuleFlatSerializer(ModuleSerializer):
    class Meta:
        model = Modules
        fields = ['module_code', 'name', 'examination', 'supervisor',
                  'lectures_hours', 'laboratory_classes_hours', 'auditorium_classes_hours', 'project_classes_hours',
                  'seminar_classes_hours']


class SupervisedModuleSerializer(ModuleSerializer, NestedHyperlinkedModelSerializer):
    """
    Supervised Module Serializer - helper Serializer for nesting in the Employee Serializer
    """
    class Meta:
        model = Modules
        fields = ['url',
                  'module_code', 'name', 'examination',
                  # hidden fields:
                  'supervisor']
        extra_kwargs = {
            # url's custom lookup - needs to match lookup set in the view set
            'url': {
                'view_name': 'employee-modules-detail',
                'lookup_field': 'module_code',
            },
        }
    parent_lookup_kwargs = {
        'employee_abbreviation': 'supervisor__abbreviation'
    }

    # Requested URL should point one parent object - in this case supervisor
    supervisor = GetParentHiddenField(
        queryset=Employees.objects.all(),
        parent_lookup_kwargs={'employee_abbreviation': 'abbreviation'},
    )
