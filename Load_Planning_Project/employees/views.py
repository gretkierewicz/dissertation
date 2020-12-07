import re

from csv import DictReader
from io import StringIO

from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from rest_framework.status import HTTP_303_SEE_OTHER
from rest_framework.decorators import action
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_csv.renderers import CSVRenderer

from .models import Degrees, Positions, Employees
from .serializers import DegreeSerializer, PositionSerializer, EmployeeSerializer


class DegreeViewSet(ModelViewSet):
    queryset = Degrees.objects.all().order_by('name')
    serializer_class = DegreeSerializer

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context['header'] = (['name'])
        return context

    @action(detail=False, methods=['POST'])
    def bulk_upload(self, request):
        serializer = self.get_serializer()
        if len(request.FILES) != 0:
            for key in request.FILES.keys():
                csv_dict = DictReader(StringIO(request.data.get(key).read().decode('UTF-8')), delimiter=',')
                for row in csv_dict:
                    try:
                        Degrees.objects.get(name=row.get('name'))
                        continue
                    except ObjectDoesNotExist:
                        serializer = self.get_serializer(data=row)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
        return Response(serializer.data, status=HTTP_303_SEE_OTHER, headers={'Location': reverse('degrees-list')})


class PositionViewSet(ModelViewSet):
    queryset = Positions.objects.all().order_by('name')
    serializer_class = PositionSerializer

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context['header'] = (['name'])
        return context

    @action(detail=False, methods=['POST'])
    def bulk_upload(self, request):
        serializer = self.get_serializer()
        if len(request.FILES) != 0:
            for key in request.FILES.keys():
                csv_dict = DictReader(StringIO(request.data.get(key).read().decode('UTF-8')), delimiter=',')
                for row in csv_dict:
                    try:
                        Positions.objects.get(name=row.get('name'))
                        continue
                    except ObjectDoesNotExist:
                        serializer = self.get_serializer(data=row)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
        return Response(serializer.data, status=HTTP_303_SEE_OTHER, headers={'Location': reverse('positions-list')})


class EmployeeRenderer(CSVRenderer):
    header = ['first_name', 'last_name', 'abbreviation', 'degree_repr', 'position_repr', 'e_mail',
              'supervisor_repr', 'year_of_studies', 'is_procedure_for_a_doctoral_degree_approved', 'has_scholarship']
    labels = {
        'degree_repr': 'degree',
        'position_repr': 'position',
        'supervisor_repr': 'supervisor'
    }


class EmployeeViewSet(ModelViewSet):
    queryset = Employees.objects.all().order_by('abbreviation')
    serializer_class = EmployeeSerializer
    renderer_classes = (BrowsableAPIRenderer, JSONRenderer, EmployeeRenderer, )

    @action(detail=False, methods=['PUT', 'POST'])
    def bulk_upload(self, request):
        serializer = self.get_serializer()
        if len(request.FILES) != 0:
            for key in request.FILES.keys():
                csv_dict = DictReader(StringIO(request.data.get(key).read().decode('UTF-8')), delimiter=',')
                for row in csv_dict:
                    try:
                        degree = Degrees.objects.get(name=row.get('degree')).pk
                        row['degree'] = request.build_absolute_uri(reverse('degrees-detail', args=[degree]))
                    except ObjectDoesNotExist:
                        row['degree'] = None
                    try:
                        position = Positions.objects.get(name=row.get('position')).pk
                        row['position'] = request.build_absolute_uri(reverse('positions-detail', args=[position]))
                    except ObjectDoesNotExist:
                        row['position'] = None
                    try:
                        supervisor = Employees.objects.get(abbreviation=row.get('supervisor')).pk
                        row['supervisor'] = request.build_absolute_uri(reverse('employees-detail', args=[supervisor]))
                    except ObjectDoesNotExist:
                        row['supervisor'] = None

                    year_of_studies = re.match(r'\d+', row.get('year_of_studies'))
                    row['year_of_studies'] = year_of_studies.group() if year_of_studies else None

                    try:
                        employee = Employees.objects.get(e_mail=row.get('e_mail'))
                        # with POST only create new entries, with PUT - update existing ones
                        if request.method == 'POST':
                            continue
                        serializer = self.get_serializer(employee, data=row)
                    except ObjectDoesNotExist:
                        serializer = self.get_serializer(data=row)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
        return Response(serializer.data, status=HTTP_303_SEE_OTHER, headers={'Location': reverse('employees-list')})
