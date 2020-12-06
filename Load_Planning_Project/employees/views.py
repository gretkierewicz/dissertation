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

