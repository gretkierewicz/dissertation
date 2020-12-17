import re

from csv import DictReader
from io import StringIO

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.status import HTTP_303_SEE_OTHER
from rest_framework_csv.renderers import CSVRenderer

from .models import Degrees, Positions, Employees, Modules, Orders
from .serializers import DegreeSerializer, PositionSerializer, EmployeeSerializer, ModuleSerializer, OrderSerializer, \
    DegreeShortSerializer, PositionShortSerializer, EmployeeShortSerializer


class DegreeViewSet(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.ListModelMixin,
                    GenericViewSet):
    # disallow DELETE for that view
    queryset = Degrees.objects.all().order_by('name')
    serializer_class = DegreeSerializer

    def list(self, request, *args, **kwargs):
        queryset = Degrees.objects.all()
        serializer = DegreeShortSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context['header'] = (['name'])
        return context

    @action(detail=False, methods=['POST'])
    def csv_files_upload(self, request):
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


class PositionViewSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.ListModelMixin,
                      GenericViewSet):
    queryset = Positions.objects.all().order_by('name')
    serializer_class = PositionSerializer

    def list(self, request, *args, **kwargs):
        queryset = Positions.objects.all()
        serializer = PositionShortSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context['header'] = (['name'])
        return context

    @action(detail=False, methods=['POST'])
    def csv_files_upload(self, request):
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
    lookup_field = 'abbreviation'

    def list(self, request, *args, **kwargs):
        queryset = Employees.objects.all()
        serializer = EmployeeShortSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['PUT', 'POST'])
    def csv_files_upload(self, request):
        serializer = self.get_serializer()
        if len(request.FILES) != 0:
            for key in request.FILES.keys():
                csv_dict = DictReader(StringIO(request.data.get(key).read().decode('UTF-8')), delimiter=',')
                for row in csv_dict:
                    try:
                        degree = Degrees.objects.get(name=row.get('degree'))
                        row['degree'] = request.build_absolute_uri(
                            reverse('degrees-detail',
                                    kwargs={'pk': degree.pk}))
                    except ObjectDoesNotExist:
                        row['degree'] = None
                    try:
                        position = Positions.objects.get(name=row.get('position'))
                        row['position'] = request.build_absolute_uri(
                            reverse('positions-detail',
                                    kwargs={'pk': position.pk}))
                    except ObjectDoesNotExist:
                        row['position'] = None
                    try:
                        supervisor = Employees.objects.get(abbreviation=row.get('supervisor'))
                        row['supervisor'] = request.build_absolute_uri(
                            reverse('employees-detail',
                                    kwargs={'abbreviation': supervisor.abbreviation}
                                    ))
                    except ObjectDoesNotExist:
                        row['supervisor'] = None

                    year_of_studies = re.match(r'\d+', row.get('year_of_studies'))
                    row['year_of_studies'] = year_of_studies.group() if year_of_studies else None

                    try:
                        # with POST only create new entries, with PUT - only update existing ones
                        employee = Employees.objects.get(e_mail=row.get('e_mail'))
                        if request.method == 'PUT':
                            serializer = self.get_serializer(employee, data=row)
                            serializer.is_valid(raise_exception=True)
                            serializer.save()
                    except ObjectDoesNotExist:
                        if request.method == 'POST':
                            serializer = self.get_serializer(data=row)
                            serializer.is_valid(raise_exception=True)
                            serializer.save()
        return Response(serializer.data, status=HTTP_303_SEE_OTHER, headers={'Location': reverse('employees-list')})


class ModuleViewSet(ModelViewSet):
    queryset = Modules.objects.all().order_by('code')
    serializer_class = ModuleSerializer
    lookup_field = 'code'


class OrderViewSet(ModelViewSet):
    queryset = Orders.objects.all()
    serializer_class = OrderSerializer

    def retrieve(self, request, module=None, lesson_type=None, *args, **kwargs):
        order = get_object_or_404(
            Orders,
            module=get_object_or_404(Modules, code=module),
            lesson_type=lesson_type,
        )
        serializer = OrderSerializer(order)
        serializer.context['request'] = request
        return Response(serializer.data)
