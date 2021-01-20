from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework_csv.renderers import CSVRenderer

from utils.serializers import read_csv_files
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
        Action to upload CSV file(s).
        POST method will try to create new records.
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
        """
        return read_csv_files(self=self, request=request, model=Positions, lookup='name')


class PensumViewSet(ModelViewSet):
    queryset = Pensum.objects.all()
    serializer_class = PensumSerializer


class EmployeeRenderer(CSVRenderer):
    """
    Custom CSV Renderer for Employee View Set
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
        return read_csv_files(self=self, request=request, model=Employees, lookup='e_mail')
