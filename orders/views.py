from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet, GenericViewSet, mixins
from rest_framework_nested.viewsets import NestedViewSetMixin

from utils.ViewSets import OneToOneRelationViewSet
from .models import Orders, Plans
from .serializers import OrdersSerializer, PlansSerializer, ClassesOrderSerializer


class OrdersViewSet(GenericViewSet,
                    mixins.ListModelMixin,
                    mixins.CreateModelMixin):
    serializer_class = OrdersSerializer

    def get_queryset(self):
        return Orders.objects.filter(classes__module__schedule__slug=self.kwargs.get('schedule_slug'))


class OrderDetailViewSet(OneToOneRelationViewSet):
    # with NestedViewSetMixin get_queryset is overridden to include Serializer's parent_lookup_kwargs
    queryset = Orders.objects.all()
    serializer_class = ClassesOrderSerializer


class PlansViewSet(NestedViewSetMixin, ModelViewSet):
    # with NestedViewSetMixin get_queryset is overridden to include Serializer's parent_lookup_kwargs
    queryset = Plans.objects.all()
    serializer_class = PlansSerializer
    lookup_field = 'employee'

    # custom object for explicit employee (nested plan's queryset for explicit order - see above)
    def get_object(self):
        return get_object_or_404(self.get_queryset(), employee__abbreviation=self.kwargs.get(self.lookup_field))
