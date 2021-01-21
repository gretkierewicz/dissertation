from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.viewsets import ModelViewSet, GenericViewSet, mixins
from rest_framework_csv.renderers import CSVRenderer

from .models import Modules, Classes, Plans
from .serializers import ModuleSerializer, ClassSerializer, PlanSerializer, SupervisedModuleSerializer, \
    EmployeePlanModulesSerializer, ModuleFlatSerializer


class ModuleRenderer(CSVRenderer):
    """
    Custom CSV Renderer for Module View Set
    Keeps proper column arrangement
    """
    header = ['module_code', 'name', 'examination', 'supervisor', 'lectures_hours', 'laboratory_classes_hours',
              'auditorium_classes_hours', 'project_classes_hours', 'seminar_classes_hours']


class ModuleViewSet(ModelViewSet):
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
            serializer = ModuleFlatSerializer(self.queryset, many=True, context={'request': request})
        else:
            serializer = ModuleSerializer(self.queryset, many=True, context={'request': request})
        return Response(serializer.data)

    # Custom retrieve method with different serializers for different formats
    def retrieve(self, request, *args, **kwargs):
        # get flat data of employee instance for CSV format
        if request.query_params.get('format') == 'csv':
            serializer = ModuleFlatSerializer(get_object_or_404(self.queryset, **kwargs), context={'request': request})
        else:
            serializer = ModuleSerializer(get_object_or_404(self.queryset, **kwargs), context={'request': request})
        return Response(serializer.data)


class EmployeeModuleViewSet(ModuleViewSet):
    """
    Employee/Module View Set
    Create, Retrieve, Update, Delete Employee's modules
    """
    serializer_class = SupervisedModuleSerializer

    # custom queryset for nested view
    def get_queryset(self):
        # employee_abbreviation needs to be set as 'lookup_url_kwarg' in module's hyperlink's parameters
        return Modules.objects.filter(supervisor__abbreviation=self.kwargs.get('employee_abbreviation'))


class ClassViewSet(ModelViewSet):
    """
    Class View Set
    Create, Retrieve, Update, Delete orders
    """
    serializer_class = ClassSerializer
    # Custom lookup_field - needs entry in extra_kwargs of serializer!
    lookup_field = 'name'

    # custom queryset for nested view
    def get_queryset(self):
        # kwarg needs to match url kwarg (router lookup + field name)
        return Classes.objects.filter(module__module_code=self.kwargs.get('module_module_code'))


class PlanViewSet(ModelViewSet):
    serializer_class = PlanSerializer
    lookup_field = 'employee'

    # custom queryset for nested view
    def get_queryset(self):
        # kwargs need to match url lookups (router lookups + field names)
        return Plans.objects.filter(classes__name=self.kwargs.get('class_name'),
                                    classes__module__module_code=self.kwargs.get('module_module_code'))

    # custom object for nested view
    def get_object(self):
        return get_object_or_404(self.get_queryset(), employee__abbreviation=self.kwargs.get(self.lookup_field))


class EmployeePlanViewSet(GenericViewSet,
                          mixins.ListModelMixin):
    serializer_class = EmployeePlanModulesSerializer

    # custom queryset for nested view
    def get_queryset(self):
        # kwargs need to match url lookups (router lookups + field names)
        return Modules.objects.filter(
            classes__plans__employee__abbreviation=self.kwargs.get('employee_abbreviation')
        ).distinct()
