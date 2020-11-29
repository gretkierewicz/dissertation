from rest_framework import serializers

from .models import Degrees, Positions, Employees


class DegreeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Degrees
        fields = ('name',)


class PositionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Positions
        fields = ('name',)


class EmployeeSerializer(serializers.ModelSerializer):
    # without these, field sent will be the 'id'
    degree = serializers.SlugRelatedField(slug_field='name', queryset=Degrees.objects.all())
    position = serializers.SlugRelatedField(slug_field='name', queryset=Positions.objects.all())
    supervisor = serializers.SlugRelatedField(slug_field='abbreviation',
                                              queryset=Employees.objects.all())

    class Meta:
        model = Employees
        # exclude = ['id']
        fields = ('first_name', 'last_name', 'abbreviation', 'degree', 'position', 'e_mail', 'supervisor',
                  'year_of_studies', 'is_procedure_for_a_doctoral_degree_approved', 'has_scholarship')

