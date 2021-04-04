import re
from collections import OrderedDict

from django.shortcuts import redirect
from django.urls import reverse
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.viewsets import ModelViewSet
from rest_framework_csv.parsers import CSVParser
from rest_framework_csv.renderers import CSVRenderer
from rest_framework_nested.viewsets import NestedViewSetMixin

from .models import Modules, Classes
from .serializers import ModuleSerializer, ClassSerializer, ModuleFlatSerializer


class ModuleRenderer(CSVRenderer):
    """
    Custom CSV Renderer for Module View Set
    Keeps proper column arrangement
    """
    classes_hours = ['lectures_hours', 'laboratory_classes_hours', 'auditorium_classes_hours', 'project_classes_hours',
                     'seminar_classes_hours']
    header = ['module_code', 'name', 'examination', 'supervisor'] + classes_hours


class ModuleViewSet(NestedViewSetMixin, ModelViewSet):
    """
    Modules View Set
    Create, Retrieve, Update, Delete modules
    """
    queryset = Modules.objects.all()
    serializer_class = ModuleSerializer
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (ModuleRenderer, )
    # Custom lookup_field - needs entry in extra_kwargs of serializer!
    lookup_field = 'module_code'

    # Custom list method with different serializers for different formats
    def list(self, request, *args, **kwargs):
        # list flat data of each employee for CSV format
        if request.query_params.get('format') == 'csv':
            serializer = ModuleFlatSerializer(self.get_queryset(), many=True, context={'request': request})
        else:
            serializer = ModuleSerializer(self.get_queryset(), many=True, context={'request': request})
        return Response(serializer.data)

    # Custom retrieve method with different serializers for different formats
    def retrieve(self, request, *args, **kwargs):
        # get flat data of employee instance for CSV format
        if request.query_params.get('format') == 'csv':
            serializer = ModuleFlatSerializer(instance=self.get_object(), context={'request': request})
        else:
            serializer = ModuleSerializer(instance=self.get_object(), context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['PUT', 'POST'])
    def csv_files_upload(self, request):
        """
        Action to upload CSV file(s).
        POST method will try to create new records.
        PUT method will update existing or create new records.
        Module possible column headers: 'module_code', 'name', 'examination', 'supervisor'
        'supervisor' - must be provided by his abbreviation
        Additional classes possible column headers. If column will be present with empty value, existing classes
        instance will be deleted! Put 0 instead to save from deletion.): 'lectures_hours', 'laboratory_classes_hours',
        'auditorium_classes_hours', 'project_classes_hours', 'seminar_classes_hours'
        """
        if request.FILES:
            data = {}
            lookup = 'module_code'
            for file in request.FILES:
                data[file + ' file'] = {}
                for file_data in CSVParser.parse(self, stream=request.data.get(file)):
                    for key, value in file_data.items():
                        # convert empty strings into None
                        file_data[key] = value if value else None
                    partial_data = OrderedDict(file_data)
                    if request.method == 'PUT':
                        instance = self.get_queryset().filter(**{lookup: partial_data[lookup]}).first()
                        serializer = self.get_serializer(instance, data=partial_data)
                    else:
                        serializer = self.get_serializer(data=partial_data)
                    if serializer.is_valid():
                        serializer.save()
                        deleted_classes = []
                        # additional logic to create/update classes in the module instance
                        for rec in ModuleRenderer.classes_hours:
                            # filter name - rip of '_hours' from column's header
                            classes = serializer.instance.classes.filter(name=rec[:-6].capitalize()).first()
                            # classes columns should contain number, if not - pass None
                            value = re.search(r'\d+', partial_data.get(rec))
                            if value:
                                value = int(value.group())
                            # in case of missing value in column classes instance will be deleted!
                            if classes and (rec in partial_data) and value is not None:
                                classes.classes_hours = value
                                classes.save()
                            # 2nd condition ensures that instance will be deleted only if column is present in CSV file
                            elif classes and (rec in partial_data):
                                classes.delete()
                                # save names for informational display
                                deleted_classes.append(rec[:-6].capitalize())
                            # if no classes instance but got value for it - create new instance
                            elif value is not None:
                                Classes.objects.create(module=serializer.instance, name=rec[:-6].capitalize(),
                                                       classes_hours=value)
                        # at this point serializer data will be read for updated module instance
                        data[file + ' file'][partial_data.get(lookup)] = [serializer.data]
                        # simple additional information about deleted classes (only for response)
                        for classes in deleted_classes:
                            data[file + ' file'][partial_data.get(lookup)][0]['classes'].append({
                                'name': classes, 'status': 'deleted'})
                    if serializer.errors:
                        data[file + ' file'][partial_data.get(lookup)] = [serializer.errors]
            return Response(data)


class ClassViewSet(NestedViewSetMixin, ModelViewSet):
    """
    Class View Set
    Create, Retrieve, Update, Delete orders
    """
    # with NestedViewSetMixin get_queryset is overridden to include Serializer's parent_lookup_kwargs
    queryset = Classes.objects.all()
    serializer_class = ClassSerializer
    # Custom lookup_field - needs entry in extra_kwargs of serializer!
    lookup_field = 'name'

    @action(detail=True)
    # additional action to make creation of order easier accessible
    def new_order(self, *args, **kwargs):
        kwargs['classes_name'] = kwargs.pop('name')
        return redirect(reverse(viewname='classes-order-detail', kwargs=kwargs))
