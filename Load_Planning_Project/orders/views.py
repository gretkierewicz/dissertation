from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet, GenericViewSet, mixins

from .models import Orders, Plans
from .serializers import OrdersSerializer, PlansSerializer, ClassesOrderSerializer


class OrdersViewSet(GenericViewSet,
                    mixins.ListModelMixin,
                    mixins.CreateModelMixin):
    # return different queryset for nested view and full for not nested
    def get_queryset(self):
        if self.kwargs.get('module_module_code') and self.kwargs.get('class_name'):
            return Orders.objects.filter(
                classes__module__module_code=self.kwargs.get('module_module_code'),
                classes__name=self.kwargs.get('class_name')
            )
        return Orders.objects.all()

    # return nested serializer (classes hidden) for nested view and full for not nested
    def get_serializer_class(self):
        if self.kwargs.get('module_module_code') and self.kwargs.get('class_name'):
            return ClassesOrderSerializer
        return OrdersSerializer


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
