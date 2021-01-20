from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from rest_framework.generics import get_object_or_404
from rest_framework.relations import HyperlinkedIdentityField
from rest_framework.serializers import HyperlinkedModelSerializer
from rest_framework_nested.relations import NestedHyperlinkedIdentityField
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer

from utils.serializers import ParentFromURLHiddenField, SerializerLambdaField

from .models import Modules, Classes, Plans
from employees.models import Employees


class PlanSerializer(NestedHyperlinkedModelSerializer):
    """
    Plan Serializer - Main Plan Serializer with implemented validation
    """
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
            'plan_hours': {'min_value': 1}
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

    def validate_plan_hours(self, data):
        # validation of plan's hours if summary classes' hours are not exceeded
        # retrieve parent classes from request url
        url_kwargs = self.context['request'].resolver_match.kwargs
        filter_kwargs = {'module__module_code': url_kwargs['module_module_code'], 'name': url_kwargs['class_name']}
        classes = get_object_or_404(Classes, **filter_kwargs)
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
        fields = ['url', 'name', 'classes_hours', 'classes_hours_not_set', 'plans_url', 'plans',
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
    module = ParentFromURLHiddenField(
        # queryset that will be filtered
        queryset=Modules.objects.all(),
        # key is a parent_lookup_kwarg, value - a field to filter by
        matches={'module_module_code': 'module_code'},
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

    supervisor_repr = SerializerLambdaField(lambda obj: '{}'.format(obj.supervisor))

    classes_url = HyperlinkedIdentityField(
        view_name='classes-list',
        lookup_field='module_code',
        lookup_url_kwarg='module_module_code',
    )
    # needs parent_lookup_kwargs configured in nested serializer!
    classes = ClassSerializer(read_only=True, many=True)


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
    supervisor = ParentFromURLHiddenField(
        queryset=Employees.objects.all(),
        matches={'employee_abbreviation': 'abbreviation'},
    )


class EmployeePlanClassSerializer(ClassSerializer):
    """
    Employee Plan Class Serializer - helper Serializer for nesting in the Employee Plan Serializer
    """
    class Meta:
        model = Classes
        fields = ['name', 'classes_hours', 'employee_plan_hours']

    # for Classes instance it is enough to only get one plan_hours as only one Employee is given
    employee_plan_hours = SerializerMethodField('get_plan_hours')

    def get_plan_hours(self, obj):
        # in Classes instance find plan related to the Employee (cannot use get_object_or_404 here because of 404 error)
        plan = obj.plans.filter(
            # logical OR needed because of URL kwargs naming differences:
            # 'employee-detail' vs 'employee-plans-list' url patterns
            employee__abbreviation=(self.context['request'].resolver_match.kwargs.get('abbreviation') or
                                    self.context['request'].resolver_match.kwargs.get('employee_abbreviation'))
            # with given Employee, for each Classes instance, there should be always exactly 1 plan filtered!
        ).first()
        # there should be not even one Classes instance with no plan for given Employee thanks to overwriting
        # 'to_representation' method in parent's Serializer (EmployeePlanSerializer)
        # But in case if no plan found - return 0
        return plan.plan_hours if plan else 0


class EmployeePlanSerializer(ModuleSerializer):
    """
    Employee Plan Serializer - helper Plan Serializer that includes only Classes with setup hours for specific Employee
    To be nested into the Employee Serializer
    """
    class Meta:
        model = Modules
        fields = ['url', 'module_code', 'name',
                  'classes', 'examination',
                  'supervisor', 'supervisor_repr']
        extra_kwargs = {
            # url's custom lookup - needs to match lookup set in the view set
            'url': {'lookup_field': 'module_code'},
            'supervisor': {'lookup_field': 'abbreviation'}
        }

    classes = EmployeePlanClassSerializer(read_only=True, many=True)

    def to_representation(self, instance):
        odict_obj = super().to_representation(instance)
        # remove Classes instances with no plan hours for given Employee
        odict_obj['classes'] = [
            classes_obj for classes_obj in odict_obj['classes'] if classes_obj.get('employee_plan_hours') > 0
        ]
        return odict_obj
