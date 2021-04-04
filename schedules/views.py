from rest_framework.viewsets import ModelViewSet

from .models import Schedules
from .serializers import ScheduleSerializer


class SchedulesViewSet(ModelViewSet):
    """
    Schedules View Set
    Create, Retrieve, Update, Delete custom schedules for employees-modules organization
    """
    queryset = Schedules.objects.all()
    serializer_class = ScheduleSerializer
    # Custom lookup_field - needs entry in extra_kwargs of serializer!
    lookup_field = 'slug'
