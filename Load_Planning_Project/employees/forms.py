from django.forms import ModelForm, TextInput

from .models import Degrees, Positions


class DegreeForm(ModelForm):
    class Meta:
        model = Degrees
        fields = ['name']
        widgets = {
            'name': TextInput(attrs={'size': 5})
        }


class PositionForm(ModelForm):
    class Meta:
        model = Positions
        fields = ['name']
        widgets = {
            'name': TextInput(attrs={'size': 5})
        }
