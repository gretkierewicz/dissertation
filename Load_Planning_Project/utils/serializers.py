from collections import OrderedDict

from rest_framework.fields import SerializerMethodField, HiddenField
from rest_framework.response import Response
from rest_framework_csv.parsers import CSVParser


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
