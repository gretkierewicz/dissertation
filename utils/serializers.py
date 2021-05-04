from collections import OrderedDict

from rest_framework.fields import SerializerMethodField
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


class SerializerLambdaField(SerializerMethodField):
    """
    Source: https://blog.ridmik.com/a-cleaner-alternative-to-serializermethodfield-in-django/
    SerializerLambdaField - Custom Serializer Method Field
    Allows use of lambda function as parameter
    """

    def bind(self, field_name, parent):
        super(SerializerMethodField, self).bind(field_name, parent)

    def to_representation(self, data):
        return self.method_name(data)
