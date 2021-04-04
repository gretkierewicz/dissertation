from rest_framework.relations import HyperlinkedIdentityField

from .models import Schedules
from modules.serializers import ModuleSerializer


class ScheduleSerializer(ModuleSerializer):
    class Meta:
        model = Schedules
        fields = ['url', 'slug', 'modules_url', 'orders_url']

    url = HyperlinkedIdentityField(view_name='schedules-detail', lookup_field='slug')

    modules_url = HyperlinkedIdentityField(
        view_name='modules-list',
        lookup_field='slug',
        lookup_url_kwarg='schedule_slug'
    )
    orders_url = HyperlinkedIdentityField(
        view_name='orders-list',
        lookup_field='slug',
        lookup_url_kwarg='schedule_slug'
    )
