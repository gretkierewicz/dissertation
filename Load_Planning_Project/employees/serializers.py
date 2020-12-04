from rest_framework import serializers

from .models import Degrees, Positions, Employees


class DegreeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Degrees
        fields = '__all__'


class PositionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Positions
        fields = '__all__'


class EmployeeSerializer(serializers.HyperlinkedModelSerializer):
    degree = serializers.HyperlinkedRelatedField(
        view_name='degrees-detail', queryset=Degrees.objects.all().order_by('name')
    )
    position = serializers.HyperlinkedRelatedField(
        view_name='positions-detail', queryset=Positions.objects.all().order_by('name')
    )
    supervisor = serializers.HyperlinkedRelatedField(
        view_name='employees-detail', queryset=Employees.objects.all().order_by('abbreviation'), allow_null=True
    )

    def validate_supervisor(self, data):
        if self.initial_data['abbreviation'] == data.abbreviation:
            raise serializers.ValidationError("Cannot self reference that field!")
        return data

    class Meta:
        model = Employees
        fields = '__all__'
