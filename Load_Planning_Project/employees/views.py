from rest_framework import viewsets

from .models import Degrees, Positions, Employees
from .serializers import DegreeSerializer, PositionSerializer, EmployeeSerializer


class DegreeViewSet(viewsets.ModelViewSet):
    queryset = Degrees.objects.all().order_by('name')
    serializer_class = DegreeSerializer


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Positions.objects.all().order_by('name')
    serializer_class = PositionSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employees.objects.all().order_by('abbreviation')
    serializer_class = EmployeeSerializer
