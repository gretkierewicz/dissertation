from rest_framework import mixins
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from .models import Modules, Classes, Plans
from .serializers import ModuleSerializer, ClassSerializer, PlanSerializer


class ModulesByEmployeeViewSet(GenericViewSet,
                               mixins.ListModelMixin,
                               mixins.RetrieveModelMixin):
    """
    Employee/Module View Set
    Nested View Set to display employee's modules
    Only Retrieve allowed (read only)
    """
    serializer_class = ModuleSerializer
    # Custom lookup_field - needs entry in extra_kwargs of serializer!
    lookup_field = 'module_code'

    # custom queryset for nested view
    def get_queryset(self):
        # employee_abbreviation needs to be set as 'lookup_url_kwarg' in module's hyperlink's parameters
        return Modules.objects.filter(supervisor__abbreviation=self.kwargs.get('employee_abbreviation'))


class ModuleViewSet(ModelViewSet):
    """
    Modules View Set
    Create, Retrieve, Update, Delete modules
    """
    queryset = Modules.objects.order_by('module_code')
    serializer_class = ModuleSerializer
    # Custom lookup_field - needs entry in extra_kwargs of serializer!
    lookup_field = 'module_code'


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
        print(self.kwargs)
        # kwargs need to match url lookups (router lookups + field names)
        return Plans.objects.filter(
            classes__name=self.kwargs.get('class_name'),
            classes__module__module_code=self.kwargs.get('module_module_code'),
        )

    # custom object for nested view
    def get_object(self):
        return self.get_queryset().get(employee__abbreviation=self.kwargs.get(self.lookup_field))