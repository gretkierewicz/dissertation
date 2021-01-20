import re
from collections import OrderedDict

from csv import DictReader
from io import StringIO

from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.status import HTTP_200_OK, HTTP_303_SEE_OTHER
from rest_framework_csv.parsers import CSVParser
from rest_framework_csv.renderers import CSVRenderer

from .models import Degrees, Positions, Employees, Pensum
from .serializers import DegreeSerializer, PositionSerializer, EmployeeListSerializer, EmployeeSerializer, \
    PensumSerializer


class DegreeViewSet(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.ListModelMixin,
                    GenericViewSet):
    """
    Degrees View Set
    Create, Retrieve, Update degrees
    Deleting not allowed
    """
    queryset = Degrees.objects.all()
    serializer_class = DegreeSerializer

    # Customizing header for CSV format
    def get_renderer_context(self):
        context = super().get_renderer_context()
        context['header'] = (['name'])
        return context

    # Action for uploading data in format of CSV files - based on exported CSV format
    @action(detail=False, methods=['POST'])
    def csv_files_upload(self, request):
        """
        csv_files_upload method - looks for CSV files in the request and tries to create new records with it
        Data needs to match format set in the get_renderer_context method
        New record will be created with POST method
        :param request: received CSV files
        :return: Response with serializer's data, HTTP 303, degrees-list
        """
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
    """
    Positions View Set
    Create, Retrieve, Update degrees
    Deleting not allowed
    """
    queryset = Positions.objects.all()
    serializer_class = PositionSerializer

    # Customizing header for CSV format
    def get_renderer_context(self):
        context = super().get_renderer_context()
        context['header'] = (['name'])
        return context

    # Action for uploading data in format of CSV files - based on exported CSV format
    @action(detail=False, methods=['POST'])
    def csv_files_upload(self, request):
        """
        csv_files_upload method - looks for CSV files in the request and tries to create new records with it
        Data needs to match format set in the get_renderer_context method
        New record will be created with POST method
        :param request: received CSV files
        :return: Response with serializer's data, HTTP 303, positions-list
        """
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


class PensumViewSet(ModelViewSet):
    queryset = Pensum.objects.all()
    serializer_class = PensumSerializer


class EmployeeRenderer(CSVRenderer):
    """
    Custom CSV Renderer for Employee View Set
    Choosing proper headers and changing labels for better readability
    Needs custom import CSV format action -> method csv_files_upload()
    """
    header = ['first_name', 'last_name', 'abbreviation', 'degree', 'position', 'e_mail',
              'supervisor', 'year_of_studies', 'is_procedure_for_a_doctoral_degree_approved', 'has_scholarship']


class EmployeeViewSet(ModelViewSet):
    """
    Employees View Set
    Create, Retrieve, Update, Delete employees
    """
    queryset = Employees.objects.all()
    serializer_class = EmployeeSerializer
    renderer_classes = (BrowsableAPIRenderer, JSONRenderer, EmployeeRenderer, )
    # Custom lookup_field - needs entry in extra_kwargs of serializer!
    lookup_field = 'abbreviation'

    # Custom list method with simpler serializer
    def list(self, request, *args, **kwargs):
        queryset = Employees.objects.all()
        # list full data of each employee for csv, short version otherwise
        if request.query_params.get('format') == 'csv':
            serializer = EmployeeSerializer(queryset, many=True, context={'request': request})
        else:
            serializer = EmployeeListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    # Action for uploading data in format of CSV files - match it with EmployeeRenderer
    @action(detail=False, methods=['PUT', 'POST'])
    def csv_files_upload(self, request):
        """
        Action to upload CSV file(s).
        POST method will try to create new records.
        PUT method will update existing or create new records.
        """
        if request.FILES:
            data = {}
            for file in request.FILES:
                data[file + ' file'] = {}
                for file_data in CSVParser.parse(self, stream=request.data.get(file)):
                    for key, value in file_data.items():
                        # convert empty strings into None
                        file_data[key] = value if value else None
                    partial_data = OrderedDict(file_data)
                    if request.method == 'PUT':
                        employee = Employees.objects.filter(**{'e_mail': partial_data['e_mail']}).first()
                        serializer = self.get_serializer(employee, data=partial_data)
                    else:
                        serializer = self.get_serializer(data=partial_data)
                    if serializer.is_valid():
                        serializer.save()
                        data[file + ' file'][partial_data.get('e_mail')] = [serializer.data]
                    if serializer.errors:
                        data[file + ' file'][partial_data.get('e_mail')] = [serializer.errors]
            return Response(data)
