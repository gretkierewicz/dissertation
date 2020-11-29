from rest_framework import serializers

from .models import Degrees, Positions, Employees


class DegreeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Degrees
        fields = ('name',)
