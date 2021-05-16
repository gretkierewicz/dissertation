from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_csv.renderers import CSVRenderer

from utils.serializers import read_csv_files
from .models import Degrees, Employees, Positions
from .serializers import DegreeSerializer, EmployeeListSerializer, EmployeeSerializer, PositionSerializer


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
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (CSVRenderer,)

    # Customizing header for CSV format
    def get_renderer_context(self):
        context = super().get_renderer_context()
        context['header'] = (['name'])
        return context

    # Action for uploading data in format of CSV files - based on exported CSV format
    @action(detail=False, methods=['POST'])
    def csv_files_upload(self, request):
        """
        Action to upload CSV file(s).
        POST method will try to create new records.
        Handled column headers:
         - REQUIRED:
        'name' - unique string,
        """
        return read_csv_files(self=self, request=request, model=Degrees, lookup='name')


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
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (CSVRenderer,)

    # Customizing header for CSV format
    def get_renderer_context(self):
        context = super().get_renderer_context()
        context['header'] = (['name'])
        return context

    # Action for uploading data in format of CSV files - based on exported CSV format
    @action(detail=False, methods=['POST'])
    def csv_files_upload(self, request):
        """
        Action to upload CSV file(s).
        POST method will try to create new records.
        Handled column headers:
         - REQUIRED:
        'name' - unique string,
        """
        return read_csv_files(self=self, request=request, model=Positions, lookup='name')


class EmployeeRenderer(CSVRenderer):
    """
    Custom CSV Renderer for Employee View Set
    Needs custom import CSV format action -> method csv_files_upload()
    """
    header = ['first_name', 'last_name', 'abbreviation', 'degree', 'position', 'e_mail']


class EmployeeViewSet(ModelViewSet):
    """
    Employees View Set
    Create, Retrieve, Update, Delete employees
    """
    queryset = Employees.objects.all()
    serializer_class = EmployeeSerializer
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (EmployeeRenderer,)
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
        Handled column headers:
         - REQUIRED:
        'first_name' - string,
        'last_name' - string,
        'abbreviation' - unique string,
        'degree' - string ('name' field corresponding in Degrees table),
        'position' - string ('name' field corresponding in Positions table),
        'e_mail' - unique string,
         - NOT REQUIRED:
        'pensum_group' - 'badawczo-dydaktyczna'/'dydaktyczna', default='dydaktyczna',
        'part_of_job_time' - float from 0-1 range, default=1
        """
        return read_csv_files(self=self, request=request, model=Employees, lookup='e_mail')
