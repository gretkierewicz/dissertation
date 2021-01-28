from rest_framework.viewsets import ModelViewSet

from .models import Orders, Plans
from .serializers import OrderSerializer, PlansSerializer


class OrdersViewSet(ModelViewSet):
    queryset = Orders.objects.all()
    serializer_class = OrderSerializer


class PlansViewSet(ModelViewSet):
    queryset = Plans.objects.all()
    serializer_class = PlansSerializer
