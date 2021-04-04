from rest_framework.relations import HyperlinkedIdentityField

from modules.serializers import ModuleSerializer

from .models import Schedules


class ScheduleSerializer(ModuleSerializer):
    class Meta:
        model = Schedules
        fields = ['url', 'slug', ]

    url = HyperlinkedIdentityField(view_name='schedules-detail', lookup_field='slug')
