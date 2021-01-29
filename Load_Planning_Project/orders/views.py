from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet

from .models import Orders, Plans
from .serializers import OrderSerializer, OrderPlansSerializer


class OrdersViewSet(ModelViewSet):
    queryset = Orders.objects.all()
    serializer_class = OrderSerializer


class OrderPlansViewSet(ModelViewSet):
    serializer_class = OrderPlansSerializer
    lookup_field = 'employee'

    # filtering plans for explicit order (nested view)
    def get_queryset(self):
        return Plans.objects.filter(order__pk=self.kwargs.get('order_pk'))

    # custom object for explicit employee (nested plan's queryset for explicit order - see above)
    def get_object(self):
        return get_object_or_404(self.get_queryset(), employee__abbreviation=self.kwargs.get(self.lookup_field))
