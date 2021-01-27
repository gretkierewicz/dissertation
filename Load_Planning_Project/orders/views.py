from rest_framework.viewsets import ModelViewSet

from .models import Orders
from .serializers import OrderSerializer


class OrdersViewSet(ModelViewSet):
    queryset = Orders.objects.all()
    serializer_class = OrderSerializer
