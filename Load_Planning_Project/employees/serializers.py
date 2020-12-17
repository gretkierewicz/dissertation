from rest_framework.reverse import reverse
from rest_framework.serializers import HyperlinkedModelSerializer, HyperlinkedRelatedField, SerializerMethodField
from rest_framework.serializers import ValidationError

from .models import Degrees, Positions, Employees, Modules, Orders


class SerializerLambdaField(SerializerMethodField):

    def bind(self, field_name, parent):
        super(SerializerMethodField, self).bind(field_name, parent)

    def to_representation(self, data):
        return self.method_name(data)


class OrderHyperlink(HyperlinkedRelatedField):
    view_name = 'orders-detail'

    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            'module': obj.module.code,
            'lesson_type': obj.lesson_type,
        }
        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)


class EmployeeSimpleSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Employees
        fields = ['url', 'first_name', 'last_name', 'abbreviation']
        extra_kwargs = {
            'url': {'lookup_field': 'abbreviation'},
        }


class SubModuleSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Modules
        fields = ['url', 'code', 'name']
        extra_kwargs = {
            'url': {'lookup_field': 'code'},
        }


class DegreeSimpleSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Degrees
        fields = '__all__'


class DegreeSerializer(HyperlinkedModelSerializer):
    employees = EmployeeSimpleSerializer(read_only=True, many=True)

    class Meta:
        model = Degrees
        fields = '__all__'


class PositionSimpleSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Positions
        fields = '__all__'


class PositionSerializer(HyperlinkedModelSerializer):
    employees = EmployeeSimpleSerializer(read_only=True, many=True)

    class Meta:
        model = Positions
        fields = '__all__'


class EmployeeSerializer(HyperlinkedModelSerializer):
    degree = HyperlinkedRelatedField(
        view_name='degrees-detail',
        queryset=Degrees.objects.all().order_by('name'),
    )
    degree_repr = SerializerLambdaField(lambda obj: '{}'.format(obj.degree))
    position = HyperlinkedRelatedField(
        view_name='positions-detail',
        queryset=Positions.objects.all().order_by('name'),
    )
    position_repr = SerializerLambdaField(lambda obj: '{}'.format(obj.position))
    supervisor = HyperlinkedRelatedField(
        view_name='employees-detail',
        queryset=Employees.objects.all().order_by('abbreviation'),
        allow_null=True,
        lookup_field='abbreviation',
    )
    supervisor_repr = SerializerLambdaField(lambda obj: '{}'.format(obj.supervisor))
    subordinates = EmployeeSimpleSerializer(read_only=True, many=True)
    modules = SubModuleSerializer(read_only=True, many=True)

    def validate_supervisor(self, data):
        if data:
            # supervisor's sent field is compared to user's url - cannot match!
            if self.initial_data.get('supervisor') == self.context.get('request').build_absolute_uri():
                raise ValidationError("Cannot self reference that field!")
        return data

    def validate_year_of_studies(self, data):
        # validation because of DRF mapping PositiveInteger model Field into Integer serializer Field
        if data is None:
            return data
        if data < 0:
            raise ValidationError("Only positive numbers!")
        return data

    class Meta:
        model = Employees
        fields = '__all__'
        extra_kwargs = {
            'url': {'lookup_field': 'abbreviation'},
        }


class OrderSerializer(HyperlinkedModelSerializer):
    url = SerializerMethodField('get_two_key_url')
    module = HyperlinkedRelatedField(
        view_name='modules-detail',
        queryset=Modules.objects.all().order_by('code'),
        lookup_field='code',
    )

    class Meta:
        model = Orders
        fields = '__all__'

    def get_two_key_url(self, data):
        return '{base_url}{module}_{lesson_type}'.format(
            base_url=self.context.get('request').build_absolute_uri(reverse('orders-list')),
            module=data.module,
            lesson_type=data.lesson_type,
        )


class ModuleSerializer(HyperlinkedModelSerializer):
    supervisor = HyperlinkedRelatedField(
        view_name='employees-detail',
        queryset=Employees.objects.all().order_by('abbreviation'),
        allow_null=True,
        lookup_field='abbreviation',
    )
    orders = OrderSerializer(read_only=True, many=True)

    class Meta:
        model = Modules
        fields = '__all__'
        extra_kwargs = {
            'url': {'lookup_field': 'code'},
        }
