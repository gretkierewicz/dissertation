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
    def retrieve(self, request, *args, **kwargs):
        instance = None
        try:
            instance = self.get_object()
        finally:
            # prevents sending json with null values when instance is missing
            return super().retrieve(request, *args, **kwargs) if instance else Response()

    def get_object(self):
        # for OneToOne relation - after filtering queryset with NestedViewSetMixin there is always one element in it
        return self.get_queryset().first()

    def create_or_update(self, request, *args, **kwargs):
        # PUT method - create or update instance (proper relation should be set in urls patterns)
        instance = None
        try:
            instance = self.get_object()
        finally:
            # using mixin's different methods depending on the instance's existence
            return super().update(request, *args, **kwargs) if instance else super().create(request, *args, **kwargs)
