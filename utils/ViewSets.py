from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_nested.viewsets import NestedViewSetMixin


class OneToOneRelationViewSet(NestedViewSetMixin,
                              GenericViewSet,
                              mixins.RetrieveModelMixin,
                              mixins.CreateModelMixin,
                              mixins.UpdateModelMixin,
                              mixins.DestroyModelMixin):

    def get_object(self):
        # for OneToOne relation - after filtering queryset with
        # NestedViewSetMixin there is always one element in list
        return self.get_queryset().first()

    def retrieve(self, request, *args, **kwargs):
        instance = None
        try:
            instance = self.get_object()
        finally:
            # prevents sending null values when instance is missing
            if instance:
                return super().retrieve(request, *args, **kwargs)
            return Response()

    def create_or_update(self, request, *args, **kwargs):
        # PUT method - create or update instance
        # proper relation should be set in urls patterns
        instance = None
        try:
            instance = self.get_object()
        finally:
            # mixin's different methods
            # depending on instance's existence
            if instance:
                return super().update(request, *args, **kwargs)
            else:
                return super().create(request, *args, **kwargs)
