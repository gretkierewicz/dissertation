from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer

from orders.serializers import ClassesOrderSerializer
from schedules.models import Schedules
from utils.relations import AdvNestedHyperlinkedIdentityField, ParentHiddenRelatedField
from .models import Classes, Modules


class ClassSerializer(NestedHyperlinkedModelSerializer):
    """
    Class Serializer - only for nesting in the Module Serializer
    """

    class Meta:
        model = Classes
        fields = ['url', 'name', 'classes_hours', 'students_limit_per_group', 'order_url', 'order',
                  # hidden fields:
                  'module']
        extra_kwargs = {
            'classes_hours': {'min_value': 0},
            'students_limit_per_group': {'min_value': 0},
        }

    # for nesting serializer - dict of URL lookups and queryset kwarg keys
    parent_lookup_kwargs = {
        'schedule_slug': 'module__schedule__slug',
        'module_module_code': 'module__module_code',
    }

    url = AdvNestedHyperlinkedIdentityField(
        view_name='classes-detail',
        lookup_field='name',
        lookup_url_kwarg='name',
        parent_lookup_kwargs=parent_lookup_kwargs
    )

    order_url = AdvNestedHyperlinkedIdentityField(
        view_name='classes-order-detail',
        lookup_field='name',
        lookup_url_kwarg='classes_name',
        parent_lookup_kwargs=parent_lookup_kwargs
    )
    order = ClassesOrderSerializer(read_only=True)

    # New type of Field made - module should be never provided by the user!
    # Requested URL should point one parent object - in this case module's code
    module = ParentHiddenRelatedField(
        # queryset that will be filtered
        queryset=Modules.objects.all(),
        # key is a parent_lookup_kwarg, value - a field to filter by
        parent_lookup_kwargs={'module_module_code': 'module_code'},
        allow_null=True
    )


class ModuleSerializer(NestedHyperlinkedModelSerializer):
    """
    Module Serializer - serializer with url, some of the model's fields and additional properties:
    form_of_classes - nested serializer of module's classes
    """

    class Meta:
        model = Modules
        fields = ['url',
                  'module_code', 'name',
                  'examination', 'language',
                  'form_of_classes_url', 'form_of_classes',
                  # hidden
                  'schedule']
        extra_kwargs = {
            # url's custom lookup - needs to match lookup set in the view set
            'url': {'lookup_field': 'module_code'},
        }

    parent_lookup_kwargs = {
        'schedule_slug': 'schedule__slug'
    }

    url = AdvNestedHyperlinkedIdentityField(
        view_name='modules-detail',
        lookup_field='module_code',
        lookup_url_kwarg='module_code',
        parent_lookup_kwargs=parent_lookup_kwargs
    )

    form_of_classes_url = AdvNestedHyperlinkedIdentityField(
        view_name='classes-list',
        lookup_field='module_code',
        lookup_url_kwarg='module_module_code',
        parent_lookup_kwargs=parent_lookup_kwargs
    )
    # needs parent_lookup_kwargs configured in nested serializer!
    form_of_classes = ClassSerializer(read_only=False, many=True)

    schedule = ParentHiddenRelatedField(
        queryset=Schedules.objects.all(),
        parent_lookup_kwargs={
            'schedule_slug': 'slug'
        }
    )

    # overwrite for handling nested classes (this will not delete missing classes in data)
    def create(self, validated_data):
        form_of_classes = validated_data.pop('form_of_classes')
        module = Modules.objects.create(**validated_data)
        for classes_data in form_of_classes:
            classes_data['module'] = module
            Classes.objects.create(**classes_data)
        return module

    # overwrite for handling nested classes (this will not delete missing classes in data)
    def update(self, instance, validated_data):
        form_of_classes = validated_data.pop('form_of_classes')
        Modules.objects.filter(pk=instance.pk).update(**validated_data)
        for classes_data in form_of_classes:
            classes_data['module'] = instance
            classes = Classes.objects.filter(module=instance, name=classes_data.get('name'))
            if classes:
                classes.update(**classes_data)
            else:
                Classes.objects.create(**classes_data)
        return Modules.objects.get(pk=instance.pk)


class ModuleFlatSerializer(ModuleSerializer):
    class Meta:
        model = Modules
        fields = ['module_code', 'name', 'examination',
                  'lectures_hours', 'laboratory_classes_hours', 'auditorium_classes_hours', 'project_classes_hours',
                  'seminar_classes_hours']
