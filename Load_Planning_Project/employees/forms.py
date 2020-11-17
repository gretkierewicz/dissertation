from django.forms import ModelForm

from .models import Degrees, Positions, Employees


class DegreeForm(ModelForm):
    class Meta:
        model = Degrees
        fields = '__all__'


class PositionForm(ModelForm):
    class Meta:
        model = Positions
        fields = '__all__'


class EmployeeForm(ModelForm):
    class Meta:
        model = Employees
        fields = '__all__'
