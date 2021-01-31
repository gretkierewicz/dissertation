from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet, GenericViewSet, mixins

from .models import Orders, Plans
from .serializers import OrdersSerializer, PlansSerializer, ClassesOrderSerializer


class OrdersListViewSet(GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin):
    serializer_class = OrdersSerializer
    queryset = Orders.objects.all()


class OrderDetailViewSet(GenericViewSet,
                         mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.DestroyModelMixin):
    serializer_class = ClassesOrderSerializer

    def get_object(self):
        return get_object_or_404(Orders, **{
            'classes__module__module_code': self.kwargs.get('module_module_code'),
            'classes__name': self.kwargs.get('classes_name')
        })


class PlansViewSet(ModelViewSet):
    serializer_class = PlansSerializer
    lookup_field = 'employee'

    # filtering plans for explicit order (nested view)
    def get_queryset(self):
        return Plans.objects.filter(
            order__classes__name=self.kwargs.get('classes_name'),
            order__classes__module__module_code=self.kwargs.get('module_module_code')
        )

    # custom object for explicit employee (nested plan's queryset for explicit order - see above)
    def get_object(self):
        return get_object_or_404(self.get_queryset(), employee__abbreviation=self.kwargs.get(self.lookup_field))
