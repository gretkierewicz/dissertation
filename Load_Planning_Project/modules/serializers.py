from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from rest_framework.generics import get_object_or_404
from rest_framework.relations import HyperlinkedIdentityField, SlugRelatedField
from rest_framework.serializers import HyperlinkedModelSerializer
from rest_framework_nested.relations import NestedHyperlinkedIdentityField
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer

from utils.serializers import GetParentHiddenField

from .models import Modules, Classes, Plans
from employees.models import Employees


class PlanSerializer(NestedHyperlinkedModelSerializer):
    """
    Plan Serializer - Main Plan Serializer with implemented validation
    """
    class Meta:
        model = Plans
        fields = ['url',
                  'employee', 'employee_url', 'plan_hours',
                  # hidden fields:
                  'classes']
        extra_kwargs = {
            # url's custom lookup - needs to match lookup set in the view set
            'url': {'lookup_field': 'employee'},
            'plan_hours': {'min_value': 1}
        }
    # for nesting serializer - dict of URL lookups and queryset kwarg keys
    parent_lookup_kwargs = {
        'module_module_code': 'classes__module__module_code',
        'class_name': 'classes__name',
    }

    employee = SlugRelatedField(slug_field='abbreviation', queryset=Employees.objects.all(), allow_null=True)
    employee_url = HyperlinkedIdentityField(
        view_name='employees-detail',
        lookup_field='employee',
        lookup_url_kwarg='abbreviation'
    )

    # hidden classes field - pointing parent's object
    classes = GetParentHiddenField(
        queryset=Classes.objects.all(),
        matches={
            'module_module_code': 'module__module_code',
            'class_name': 'name',
        },
        # in case no valid URL (i.e. JSON data upload) look for parent passed in create/update methods
        parent_lookup='classes',
    )

    def validate_plan_hours(self, data):
        # validation of plan's hours if summary classes' hours are not exceeded
        # retrieve parent classes from request url
        if self.context.get('request'):
            url_kwargs = self.context['request'].resolver_match.kwargs
            filter_kwargs = {'module__module_code': url_kwargs['module_module_code'], 'name': url_kwargs['class_name']}
            classes = get_object_or_404(Classes, **filter_kwargs)
        else:
            # in case of bulk data upload - classes instance moved to initial data in create/update methods
            classes = self.initial_data.get('classes')
        if classes.classes_hours_set - (self.instance.plan_hours if self.instance else 0)+data > classes.classes_hours:
            raise ValidationError(
                f"Classes' hours number cannot be exceeded by summary number of it's plans hours. "
                f"Maximum number of hours to set with {'this' if self.instance else 'new'} plan: "
                f"{classes.classes_hours-classes.classes_hours_set+(self.instance.plan_hours if self.instance else 0)}"
            )
        return data

    def validate(self, attrs):
        # validation of employee's sum of overall plan's hours
        employee = attrs.get('employee') or (self.instance.employee if self.instance else None)
        set_plan_hours = attrs.get('plan_hours') or (self.instance.plan_hours if self.instance else None)
        if self.instance and self.instance.employee == employee:
            # correct to the relative set value (from actually set one)
            set_plan_hours -= self.instance.plan_hours
        # not allowing exceeding employee's pensum limit provided by degree and position
        if employee.plan_hours_sum + set_plan_hours > employee.pensum_limit:
            raise ValidationError(
                f"Provided value will exceed employee's pensum limit ({employee.pensum_limit}). Maximum value to set "
                f"for {employee.first_name} ({employee.abbreviation}) with {'this' if self.instance else 'new'} plan: "
                f"{employee.pensum_limit-employee.plan_hours_sum+(self.instance.plan_hours if self.instance else 0)}")
        return attrs


class ClassSerializer(NestedHyperlinkedModelSerializer):
    """
    Class Serializer - only for nesting in the Module Serializer
    """
    class Meta:
        model = Classes
        fields = ['url', 'name', 'classes_hours', 'classes_hours_set', 'is_class_full', 'plans_url', 'plans',
                  # hidden fields:
                  'module']
        extra_kwargs = {
            # url's custom lookup - needs to match lookup set in the view set
            'url': {'lookup_field': 'name'},
            'classes_hours': {'min_value': 0}
        }
    # for nesting serializer - dict of URL lookups and queryset kwarg keys
    parent_lookup_kwargs = {
        'module_module_code': 'module__module_code',
    }

    # New type of Field made - module should be never provided by the user!
    # Requested URL should point one parent object - in this case module's code
    module = GetParentHiddenField(
        # queryset that will be filtered
        queryset=Modules.objects.all(),
        # key is a parent_lookup_kwarg, value - a field to filter by
        matches={'module_module_code': 'module_code'},
        # in case of no valid URL (i.e. JSON data upload) look for parent passed in create/update methods
        parent_lookup='module',
    )

    # url for plans: parent's lookup_field (ClassesView); lookup_url_kwarg - lookup from URL that points lookup_field;
    # parent_lookup_kwargs - URL lookup and queryset key (parent_lookup_kwargs of this serializer)
    plans_url = NestedHyperlinkedIdentityField(
        view_name='plans-list',
        lookup_field='name',
        lookup_url_kwarg='class_name',
        parent_lookup_kwargs={
            'module_module_code': 'module__module_code',
        },
    )
    # needs parent_lookup_kwargs configured in nested serializer (only for auto-hyperlinking)
    plans = PlanSerializer(read_only=True, many=True)

    # overwrite for handling nested plans (this will not delete missing plans in data)
    def create(self, validated_data):
        classes = super().create(validated_data)
        if self.initial_data.get('plans'):
            for plans_data in self.initial_data.get('plans'):
                # as there is no valid request url to check - need to pass classes instance as parent
                plans_data['classes'] = classes
                serializer = PlanSerializer(
                    instance=classes.plans.filter(employee__abbreviation=plans_data.get('employee')).first(),
                    data=plans_data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    # TODO: need to pass this somehow to user:
                    print(serializer.errors)
        return classes

    # overwrite for handling nested plans (this will not delete missing plans in data)
    def update(self, instance, validated_data):
        classes = super().update(instance, validated_data)
        if self.initial_data.get('plans'):
            for plans_data in self.initial_data.get('plans'):
                # additionally passing classes instance for plans hours validation
                plans_data['classes'] = classes
                serializer = PlanSerializer(
                    instance=classes.plans.filter(employee__abbreviation=plans_data.get('employee')).first(),
                    data=plans_data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    # TODO: need to pass this somehow to user:
                    print(serializer.errors)
        return classes


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
                'parent_lookup_kwargs': {
                    'employee_abbreviation': 'supervisor__abbreviation',
                },
            },
        }

    # Requested URL should point one parent object - in this case supervisor
    supervisor = GetParentHiddenField(
        queryset=Employees.objects.all(),
        matches={'employee_abbreviation': 'abbreviation'},
    )


class EmployeePlanClassesSerializer(ClassSerializer):
    """
    Employee Plan Class Serializer - helper Serializer for nesting in the Employee Plan Serializer
    """
    class Meta:
        model = Classes
        fields = ['url', 'name', 'classes_hours', 'employee_plan_hours', 'plans_url', 'plans']

    url = NestedHyperlinkedIdentityField(
        view_name='classes-detail',
        lookup_field='name',
        lookup_url_kwarg='name',
        parent_lookup_kwargs={
            'module_module_code': 'module__module_code',
        }
    )
    # for Classes instance it is enough to only get one plan_hours as only one Employee is given
    employee_plan_hours = SerializerMethodField()

    def get_employee_plan_hours(self, obj):
        # in Classes instance find plan related to the Employee (cannot use get_object_or_404 here because of 404 error)
        plan = obj.plans.filter(
            # logical OR needed because of URL kwargs naming differences:
            # 'employee-detail' vs 'employee-plans-list' url patterns
            employee__abbreviation=(self.context['request'].resolver_match.kwargs.get('abbreviation') or
                                    self.context['request'].resolver_match.kwargs.get('employee_abbreviation'))
            # with given Employee, for each Classes instance, there should be always exactly 1 plan filtered!
        ).first()
        # In case if no plan found - return 0
        return plan.plan_hours if plan else 0


class EmployeePlanModulesSerializer(ModuleSerializer):
    """
    Employee Plan Serializer - helper Plan Serializer that includes only Classes with setup hours for specific Employee
    To be nested into the Employee Serializer
    """
    class Meta:
        model = Modules
        fields = ['url', 'module_code', 'name',
                  'supervisor', 'supervisor_url', 'examination',
                  'classes_url', 'classes']
        extra_kwargs = {
            # url's custom lookup - needs to match lookup set in the view set
            'url': {'lookup_field': 'module_code'},
            'supervisor': {'lookup_field': 'abbreviation'}
        }

    classes = EmployeePlanClassesSerializer(read_only=True, many=True)
