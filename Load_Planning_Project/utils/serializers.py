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


class ParentsHiddenRelatedField(HiddenField):
    """
    GetParentHiddenField - Hidden Field that returns parent object pointed with URL or passed with serializer's data
    params: queryset - queryset to find instance with
    params: parent_lookup_kwargs - parent's lookup URL kwargs names (keys) and fields (values)
    return: model instance
    """
    def __init__(self, queryset, parent_lookup_kwargs, **kwargs):
        self.queryset = queryset
        self.parent_lookup_kwargs = parent_lookup_kwargs
        kwargs['write_only'] = True
        kwargs['default'] = None
        super().__init__(**kwargs)

    def get_value(self, dictionary):
        # in case of bulk data sent return instance hidden under field's name
        # instance needs to be set up in parent's create/update methods
        if dictionary.get(self.field_name) and (dictionary.get(self.field_name) in self.queryset):
            return dictionary.get(self.field_name)
        # update data forwarded to the to_internal_value() method
        filter_kwargs = {}
        for key, value in self.parent_lookup_kwargs.items():
            # get slug from URL resolver - needs to match parent_lookup_kwargs's names!
            if self.context.get('request'):
                filter_kwargs[value] = self.context.get('request').resolver_match.kwargs.get(key)
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
