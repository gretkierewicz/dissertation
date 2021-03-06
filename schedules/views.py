from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_nested.viewsets import NestedViewSetMixin

from AGH.AGH_utils import get_pensum
from employees.models import Employees
from utils.ViewSets import OneToOneRelationViewSet
from .models import ExamsAdditionalHours, Pensum, PensumAdditionalHoursFactors, PensumBasicThresholdFactors, \
    PensumReductions, Schedules
from .serializers import ExamsAdditionalHoursSerializer, PensumAdditionalHoursFactorsSerializer, \
    PensumBasicThresholdFactorSerializer, PensumListSerializer, PensumReductionSerializer, PensumSerializer, \
    ScheduleSerializer


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

    Additional actions:
    check_and_overwrite_pensum_values_for_all_employees [POST]
    recalculate_pensum_values_for_employees_of_current_schedule [GET]
    """
    queryset = Pensum.objects.all()
    serializer_class = PensumSerializer
    # Custom lookup_field - needs entry in extra_kwargs of serializer!
    lookup_field = 'employee'

    # Custom list method with simpler serializer
    def list(self, request, *args, **kwargs):
        serializer = PensumListSerializer(self.get_queryset(), many=True, context={'request': request})
        return Response(serializer.data)

    def get_object(self):
        return self.get_queryset().filter(employee__abbreviation=self.kwargs.get(self.lookup_field)).first()

    @action(detail=False, methods=['POST'])
    def check_and_overwrite_pensum_values_for_all_employees(self, request, *args, **kwargs):
        ret = []
        for employee in Employees.objects.all():
            pensum, created = Pensum.objects.get_or_create(
                schedule=Schedules.objects.get(slug=kwargs.get('schedule_slug')),
                employee=employee
            )
            if pensum.basic_threshold != get_pensum(employee.position.name, employee.pensum_group):
                pensum.basic_threshold = get_pensum(employee.position.name, employee.pensum_group) or 0
                pensum.save()
            ret.append(
                {
                    'employee': ' '.join([employee.first_name, employee.last_name, f'({employee.abbreviation})']),
                    'position': employee.position.name,
                    'employee status': f'{"created" if created else "updated"}',
                    'pensum status': f'pensum basic threshold ({pensum.basic_threshold})'
                },
            )
        return Response(ret)

    @action(detail=False, methods=['GET'])
    def recalculate_pensum_values_for_employees_of_current_schedule(self, request, *args, **kwargs):
        ret = []
        for pensum in Pensum.objects.filter(schedule__slug=kwargs.get('schedule_slug')):
            if pensum.basic_threshold != get_pensum(pensum.employee.position.name, pensum.employee.pensum_group):
                pensum.basic_threshold = get_pensum(pensum.employee.position.name, pensum.employee.pensum_group) or 0
                pensum.save()
                ret.append(
                    {
                        'employee': ' '.join([pensum.employee.first_name, pensum.employee.last_name,
                                              f'({pensum.employee.abbreviation})']),
                        'position': pensum.employee.position.name,
                        'pensum status': f'new pensum basic threshold set ({pensum.basic_threshold})'
                    },
                )
            else:
                ret.append(
                    {
                        'employee': ' '.join([pensum.employee.first_name, pensum.employee.last_name,
                                              f'({pensum.employee.abbreviation})']),
                        'position': pensum.employee.position.name,
                        'pensum status': f'no change fo pensum basic threshold ({pensum.basic_threshold})'
                    },
                )
        return Response(ret)


class PensumBasicThresholdFactorsViewSet(NestedViewSetMixin, ModelViewSet):
    """
    Pensum Basic Threshold Factors View Set - remember that factors are calculated in order (pk).
    """
    queryset = PensumBasicThresholdFactors.objects.all()
    serializer_class = PensumBasicThresholdFactorSerializer


class PensumReductionViewSet(OneToOneRelationViewSet):
    """
    Pensum Reductions View Set - reduces pensum threshold at basis of AGH/PensumReduction.json file.
    """
    queryset = PensumReductions.objects.all()
    serializer_class = PensumReductionSerializer


class PensumAdditionalHoursFactorsViewSet(NestedViewSetMixin, ModelViewSet):
    """
    Pensum Additional Hours Factors View Set
    """
    queryset = PensumAdditionalHoursFactors.objects.all()
    serializer_class = PensumAdditionalHoursFactorsSerializer


class ExamsAdditionalHoursViewSet(NestedViewSetMixin, ModelViewSet):
    """
    Exams Additional Hours View Set
    """
    queryset = ExamsAdditionalHours.objects.all()
    serializer_class = ExamsAdditionalHoursSerializer
