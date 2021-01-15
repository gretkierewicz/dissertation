from rest_framework.exceptions import ValidationError
from rest_framework.relations import HyperlinkedIdentityField
from rest_framework.serializers import HyperlinkedModelSerializer
from rest_framework_nested.relations import NestedHyperlinkedIdentityField
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer

from utils.serializers import ParentFromURLHiddenField, SerializerLambdaField
from utils.validators import validate_if_positive

from .models import Modules, Classes, Plans


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
        # validation of plan hours that summary classes' hours are not exceeded
        # retrieve parent classes from request url
        url_kwargs = self.context['request'].resolver_match.kwargs
        filter_kwargs = {'module__module_code': url_kwargs['module_module_code'], 'name': url_kwargs['class_name']}
        classes = Classes.objects.filter(**filter_kwargs).first()
        hours_set = sum([plan.plan_hours for plan in classes.plan.all()])
        hours_to_set = hours_set - (self.instance.plan_hours if self.instance else 0) + data
        if hours_to_set > classes.classes_hours:
            raise ValidationError(
                f"Number of hours to set ({hours_to_set}) exceeds classes' hours ({classes.classes_hours}). "
                f"Maximum allowed value: "
                f"{classes.classes_hours - hours_set + (self.instance.plan_hours if self.instance else 0)}"
            )
        return data


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