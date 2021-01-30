from collections import OrderedDict
from functools import reduce

from rest_framework.fields import SerializerMethodField, HiddenField
from rest_framework.response import Response
from rest_framework_csv.parsers import CSVParser
from rest_framework_nested.relations import NestedHyperlinkedIdentityField


def read_csv_files(self, request, model, lookup):
    """
    Function reads any file uploaded and tries to serialize data into objects
    self - for serializer (get_serializer method of the ViewSet) and for CSVParser
    model + lookup - for searching already existing records
    """
    if request.FILES:
        data = {}
        for file in request.FILES:
            data[file + ' file'] = {}
            for file_data in CSVParser.parse(self, stream=request.data.get(file)):
                for key, value in file_data.items():
                    # convert empty strings into None
                    file_data[key] = value if value else None
                partial_data = OrderedDict(file_data)
                if request.method == 'PUT':
                    instance = model.objects.filter(**{lookup: partial_data[lookup]}).first()
                    serializer = self.get_serializer(instance, data=partial_data)
                else:
                    serializer = self.get_serializer(data=partial_data)
                if serializer.is_valid():
                    serializer.save()
                    data[file + ' file'][partial_data.get(lookup)] = [serializer.data]
                if serializer.errors:
                    data[file + ' file'][partial_data.get(lookup)] = [serializer.errors]
        return Response(data)


class GetParentHiddenField(HiddenField):
    """
    GetParentHiddenField - Hidden Field that returns parent object pointed with URL or passed with serializer's data
    params: queryset - object to be filtered
    params: matches - dictionary of parent's lookup URL kwargs names (keys) and parent's fields names (values)
    params: parent_lookup (optional) - lookup key in case of passing model instance with serializer's data
    return: model instance
    """
    def __init__(self, queryset, matches, parent_lookup=None, **kwargs):
        self.queryset = queryset
        self.matches = matches
        self.parent_lookup = parent_lookup
        kwargs['write_only'] = True
        kwargs['default'] = None
        super().__init__(**kwargs)

    def get_value(self, dictionary):
        # in case of bulk data sent return passed instance (needs to be set in serializers' create/update methods)
        if dictionary.get(self.parent_lookup):
            return dictionary.get(self.parent_lookup)
        # change data forwarded to the to_internal_value()
        filter_kwargs = {}
        for key, value in self.matches.items():
            # getting slug from URL resolver - needs to match parent_lookup_kwarg's names!
            if self.context.get('request'):
                filter_kwargs[value] = self.context.get('request').resolver_match.kwargs[key]
        return self.queryset.filter(**filter_kwargs).first()

    def to_internal_value(self, data):
        # return model's instance, no conversion needed
        return data


class SerializerLambdaField(SerializerMethodField):
    """
    SerializerLambdaField - Custom Serializer Method Field
    Allows use of lambda function as parameter
    """
    def bind(self, field_name, parent):
        super(SerializerMethodField, self).bind(field_name, parent)

    def to_representation(self, data):
        return self.method_name(data)


class AdvLookupNestedHyperlinkedIdentityField(NestedHyperlinkedIdentityField):
    def get_url(self, obj, view_name, request, format):
        """
        Differs from parent class only with self.lookup_field processing.
        With this version it is possible to pass lookup_field with '__' (to pass nested attributes).
        """
        if hasattr(obj, 'pk') and obj.pk in (None, ''):
            return None

        # Here it differs from parent class:
        lookups = self.lookup_field.split('__')
        lookup_value = reduce(getattr, [obj] + lookups)
        kwargs = {self.lookup_url_kwarg: lookup_value}

        # multi-level lookup
        for parent_lookup_kwarg in list(self.parent_lookup_kwargs.keys()):
            underscored_lookup = self.parent_lookup_kwargs[parent_lookup_kwarg]

            # split each lookup by their __, e.g. "parent__pk" will be split into "parent" and "pk", or
            # "parent__super__pk" would be split into "parent", "super" and "pk"
            lookups = underscored_lookup.split('__')

            # use the Django ORM to lookup this value, e.g., obj.parent.pk
            lookup_value = reduce(getattr, [obj] + lookups)

            # store the lookup_name and value in kwargs, which is later passed to the reverse method
            kwargs.update({parent_lookup_kwarg: lookup_value})

        return self.reverse(view_name, kwargs=kwargs, request=request, format=format)
