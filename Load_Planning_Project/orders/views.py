from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet, GenericViewSet, mixins
from rest_framework_nested.viewsets import NestedViewSetMixin

from .models import Orders, Plans
from .serializers import OrdersSerializer, PlansSerializer, ClassesOrderSerializer


class OrdersListViewSet(GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin):
    serializer_class = OrdersSerializer
    queryset = Orders.objects.all()


class OrderDetailViewSet(GenericViewSet,
                         mixins.RetrieveModelMixin,
                         mixins.CreateModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.DestroyModelMixin):
    serializer_class = ClassesOrderSerializer

    def get_object(self):
        return get_object_or_404(Orders, **{
            'classes__module__module_code': self.kwargs.get('module_module_code'),
            'classes__name': self.kwargs.get('classes_name')
        })

    def create_or_update(self, request, *args, **kwargs):
        # PUT method - create or update instance (proper relation is set in urls patterns)
        instance = None
        try:
            instance = self.get_object()
        finally:
            # using mixin's different methods depending on the order's instance existence
            return super().update(request, *args, **kwargs) if instance else super().create(request, *args, **kwargs)


class PlansViewSet(NestedViewSetMixin, ModelViewSet):
    # with NestedViewSetMixin get_queryset is overridden to include Serializer's parent_lookup_kwargs
    queryset = Plans.objects.all()
    serializer_class = PlansSerializer
    lookup_field = 'employee'

    # custom object for explicit employee (nested plan's queryset for explicit order - see above)
    def get_object(self):
        return get_object_or_404(self.get_queryset(), employee__abbreviation=self.kwargs.get(self.lookup_field))
