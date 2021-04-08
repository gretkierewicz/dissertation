from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_nested.viewsets import NestedViewSetMixin

from AGH.AGH_utils import get_pensum
from employees.models import Employees
from utils.ViewSets import OneToOneRelationViewSet
from .models import Schedules, Pensum, PensumFactors, PensumReductions
from .serializers import ScheduleSerializer, PensumSerializer, PensumFactorSerializer, PensumReductionSerializer


class SchedulesViewSet(ModelViewSet):
    """
    Schedules View Set
    Create, Retrieve, Update, Delete custom schedules for employees-modules organization
    """
    queryset = Schedules.objects.all()
    serializer_class = ScheduleSerializer
    # Custom lookup_field - needs entry in extra_kwargs of serializer!
    lookup_field = 'slug'


class PensumViewSet(NestedViewSetMixin, ModelViewSet):
    """
    Pensum View Set
    CRUD pensum values.
    check_and_overwrite_pensum_values - additional action to calculate basic threshold from position of employee
    """
    queryset = Pensum.objects.all()
    serializer_class = PensumSerializer
    # Custom lookup_field - needs entry in extra_kwargs of serializer!
    lookup_field = 'employee'

    def get_object(self):
        return self.get_queryset().filter(employee__abbreviation=self.kwargs.get(self.lookup_field)).first()

    @action(detail=False, methods=['GET'])
    def check_and_overwrite_pensum_values(self, request, *args, **kwargs):
        ret = []
        for employee in Employees.objects.all():
            pensum, created = Pensum.objects.get_or_create(
                schedule=Schedules.objects.get(slug=kwargs.get('schedule_slug')),
                employee=employee
            )
            pensum.basic_threshold = get_pensum(employee.position.name) or 0
            pensum.save()
            ret.append(
                {
                    'employee': ' '.join([employee.first_name, employee.last_name, f'({employee.abbreviation})']),
                    'position': employee.position.name,
                    'record created (True) or updated (False)': created,
                    'pensum basic threshold': pensum.basic_threshold
                },
            )
        return Response(ret)


class PensumFactorsViewSet(ModelViewSet):
    """
    Pensum Factors View Set - remember that factors are calculated in order (pk).
    """
    queryset = PensumFactors.objects.all()
    serializer_class = PensumFactorSerializer


class PensumReductionViewSet(OneToOneRelationViewSet):
    """
    Pensum Reductions View Set - reduces pensum threshold at basis of AGH/PensumReduction.json file.
    """
    queryset = PensumReductions.objects.all()
    serializer_class = PensumReductionSerializer
