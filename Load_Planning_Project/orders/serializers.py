from rest_framework.relations import HyperlinkedIdentityField
from rest_framework.serializers import ModelSerializer
from rest_framework.validators import UniqueValidator
from rest_framework_nested.relations import NestedHyperlinkedRelatedField

from modules.models import Classes
from .models import Orders


class OrderSerializer(ModelSerializer):
    class Meta:
        model = Orders
        fields = ['url', 'classes', 'students_number', 'groups_number', 'order_hours', 'order_number']
        extra_kwargs = {
            'students_number': {'min_value': 0}
        }

    url = HyperlinkedIdentityField(view_name='orders-detail')

    classes = NestedHyperlinkedRelatedField(
        queryset=Classes.objects.all(),
        view_name='classes-detail',
        lookup_field='name',
        parent_lookup_kwargs={
            'module_module_code': 'module__module_code'
        },
        validators=[UniqueValidator(queryset=Orders.objects.all())],
    )
