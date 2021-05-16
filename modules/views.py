from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.viewsets import ModelViewSet
from rest_framework_csv.renderers import CSVRenderer
from rest_framework_nested.viewsets import NestedViewSetMixin

from .models import Classes, Modules
from .serializers import ClassSerializer, ModuleFlatSerializer, ModuleSerializer


class ModuleRenderer(CSVRenderer):
    """
    Custom CSV Renderer for Module View Set
    Keeps proper column arrangement
    """
    classes_hours = ['lectures_hours', 'laboratory_classes_hours', 'auditorium_classes_hours', 'project_classes_hours',
                     'seminar_classes_hours']
    header = ['module_code', 'name', 'examination'] + classes_hours


class ModuleViewSet(NestedViewSetMixin, ModelViewSet):
    """
    Modules View Set
    Create, Retrieve, Update, Delete modules
    """
    queryset = Modules.objects.all()
    serializer_class = ModuleSerializer
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (ModuleRenderer,)
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data, list))
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.errors or serializer.data)


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
