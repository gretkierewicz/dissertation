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
from rest_framework.status import HTTP_200_OK, HTTP_303_SEE_OTHER
from rest_framework_csv.renderers import CSVRenderer

from .models import Degrees, Positions, Employees, Modules, Orders
from .serializers import DegreeSerializer, PositionSerializer, EmployeeSerializer, ModuleSerializer, OrderSerializer, \
    DegreeShortSerializer, PositionShortSerializer, EmployeeShortSerializer, ModuleShortSerializer, OrderShortSerializer


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

    # Custom list method with simpler serializer
    def list(self, request, *args, **kwargs):
        queryset = Degrees.objects.all().order_by('name')
        serializer = DegreeShortSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

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

    # Custom list method with simpler serializer
    def list(self, request, *args, **kwargs):
        queryset = Positions.objects.all().order_by('name')
        serializer = PositionShortSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

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


class EmployeeRenderer(CSVRenderer):
    """
    Custom CSV Renderer for Employee View Set
    Choosing proper headers and changing labels for better readability
    Needs custom import CSV format action -> method csv_files_upload()
    """
    header = ['first_name', 'last_name', 'abbreviation', 'degree_repr', 'position_repr', 'e_mail',
              'supervisor_repr', 'year_of_studies', 'is_procedure_for_a_doctoral_degree_approved', 'has_scholarship']
    labels = {
        'degree_repr': 'degree',
        'position_repr': 'position',
        'supervisor_repr': 'supervisor'
    }


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
        queryset = Employees.objects.all().order_by('abbreviation')
        # list full data of each employee for csv, short version otherwise
        if request.query_params.get('format') == 'csv':
            serializer = EmployeeSerializer(queryset, many=True, context={'request': request})
        else:
            serializer = EmployeeShortSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    # Action for uploading data in format of CSV files - match it with EmployeeRenderer
    @action(detail=False, methods=['PUT', 'POST'])
    def csv_files_upload(self, request):
        """
        csv_files_upload method - looks for CSV files in the request and tries to create/update records with it
        Data needs to match format of the EmployeeRenderer class
        Already existing records are matched by the 'e_mail' field
        New record will be created with POST method
        Already existing record will be updated with PUT method
        No action will be made in other cases
        :param request: with received CSV files preferably
        :return: response with messages about serialized data
        """
        messages = {
            'Errors': [],
        }
        if request.method == 'POST':
            messages['Created successfully'] = []
        if request.method == 'PUT':
            messages['Updated successfully'] = []
        messages['No action'] = []

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

                    # matching first number in year_of_studies field with help of regex
                    year_of_studies = re.match(r'\d+', row.get('year_of_studies'))
                    row['year_of_studies'] = year_of_studies.group() if year_of_studies else None

                    try:
                        # check if object exists by unique e_mail field
                        employee = Employees.objects.get(e_mail=row.get('e_mail'))
                        # with PUT method - update existing entry, don't create new one
                        if request.method == 'PUT':
                            serializer = self.get_serializer(employee, data=row)
                            if serializer.is_valid(raise_exception=False):
                                serializer.save()
                            if serializer.errors:
                                messages['Errors'].append({
                                    'e_mail': row.get('e_mail'),
                                    'errors': serializer.errors,
                                })
                            else:
                                messages['Updated successfully'].append({
                                    'e_mail': row.get('e_mail'),
                                })
                        else:
                            messages['No action'].append({
                                    'e_mail': row.get('e_mail'),
                                })
                    except ObjectDoesNotExist:
                        # with POST method - create new entry, do not update existing one
                        if request.method == 'POST':
                            serializer = self.get_serializer(data=row)
                            if serializer.is_valid(raise_exception=False):
                                serializer.save()
                            if serializer.errors:
                                messages['Errors'].append({
                                    'e_mail': row.get('e_mail'),
                                    'errors': serializer.errors,
                                })
                            else:
                                messages['Created successfully'].append({
                                    'e_mail': row.get('e_mail'),
                                })
                        else:
                            messages['No action'].append({
                                    'e_mail': row.get('e_mail'),
                                })

        return Response(messages, status=HTTP_200_OK)


class EmployeeModuleViewSet(GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.RetrieveModelMixin):
    """
    Employee/Module View Set
    Nested View Set to display employee's modules
    Only Retrieve allowed (read only)
    """
    serializer_class = ModuleShortSerializer
    # Custom lookup_field - needs entry in extra_kwargs of serializer!
    lookup_field = 'code'

    # custom queryset for nested view
    def get_queryset(self):
        # employee_abbreviation needs to be set as 'lookup_url_kwarg' in module's hyperlink's parameters
        return Modules.objects.all().filter(supervisor__abbreviation=self.kwargs.get('employee_abbreviation'))


class ModuleViewSet(ModelViewSet):
    """
    Modules View Set
    Create, Retrieve, Update, Delete modules
    """
    queryset = Modules.objects.all().order_by('code')
    serializer_class = ModuleSerializer
    # Custom lookup_field - needs entry in extra_kwargs of serializer!
    lookup_field = 'code'

    # Custom list method with simpler serializer
    def list(self, request, *args, **kwargs):
        queryset = Modules.objects.all().order_by('code')
        serializer = ModuleShortSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    """
    Orders View Set
    Create, Retrieve, Update, Delete orders
    """
    queryset = Orders.objects.all()
    serializer_class = OrderSerializer

    # Custom two lookup fields - needs custom url function in serializer to match it
    def retrieve(self, request, module_code=None, lesson_type=None, *args, **kwargs):
        order = get_object_or_404(
            Orders,
            module=get_object_or_404(Modules, code=module_code),
            lesson_type=lesson_type,
        )
        serializer = OrderSerializer(order)
        serializer.context['request'] = request
        return Response(serializer.data)

    # Custom list method with simpler serializer
    def list(self, request, *args, **kwargs):
        queryset = Orders.objects.order_by('module', 'lesson_type')
        serializer = OrderShortSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
