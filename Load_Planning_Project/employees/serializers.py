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
    class Meta:
        model = Employees
        fields = '__all__'
