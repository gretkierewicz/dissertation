from rest_framework.viewsets import ModelViewSet

from .models import Degrees, Positions, Employees
from .serializers import DegreeSerializer, PositionSerializer, EmployeeSerializer


class DegreeViewSet(ModelViewSet):
    queryset = Degrees.objects.all().order_by('name')
    serializer_class = DegreeSerializer


class PositionViewSet(ModelViewSet):
    queryset = Positions.objects.all().order_by('name')
    serializer_class = PositionSerializer


class EmployeeViewSet(ModelViewSet):
    queryset = Employees.objects.all().order_by('abbreviation')
    serializer_class = EmployeeSerializer

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context['header'] = (['first_name', 'last_name', 'abbreviation', 'degree_repr', 'position_repr', 'e_mail',
                              'supervisor_repr', 'year_of_studies', 'is_procedure_for_a_doctoral_degree_approved',
                              'has_scholarship'])
        return context
