from rest_framework.serializers import HyperlinkedModelSerializer, HyperlinkedRelatedField, SerializerMethodField
from rest_framework.serializers import ValidationError

from .models import Degrees, Positions, Employees


class SerializerLambdaField(SerializerMethodField):

    def bind(self, field_name, parent):
        super(SerializerMethodField, self).bind(field_name, parent)

    def to_representation(self, data):
        return self.method_name(data)


class DegreeSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Degrees
        fields = '__all__'


class PositionSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Positions
        fields = '__all__'


class EmployeeSerializer(HyperlinkedModelSerializer):
    degree = HyperlinkedRelatedField(
        view_name='degrees-detail', queryset=Degrees.objects.all().order_by('name'))
    degree_repr = SerializerLambdaField(lambda obj: '{}'.format(obj.degree))
    position = HyperlinkedRelatedField(
        view_name='positions-detail', queryset=Positions.objects.all().order_by('name'))
    position_repr = SerializerLambdaField(lambda obj: '{}'.format(obj.position))
    supervisor = HyperlinkedRelatedField(
        view_name='employees-detail', queryset=Employees.objects.all().order_by('abbreviation'), allow_null=True)
    supervisor_repr = SerializerLambdaField(lambda obj: '{}'.format(obj.supervisor))

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
