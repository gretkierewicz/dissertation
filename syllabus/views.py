import json

import requests

from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from modules.serializers import ModuleSerializer
from schedules.models import Schedules
from .serializers import SyllabusSerializer, StudyTypesSerializer, ImportModulesSerializer


class SyllabusView(GenericViewSet):
    """
    Simple form for pointing data to get from syllabus web API
    """
    serializer_class = SyllabusSerializer

    def list(self, request, *args, **kwargs):
        # just to display serializer's form without http error
        return Response()

    def post(self, request, *args, **kwargs):
        return redirect('syllabus-study_plans-list', **{
            'academic_year': request.data['academic_year'],
            'department': request.data['department']
        })


class StudyProgrammesListView(APIView):
    """
    List of study programmes for particular department and academic year
    """
    # cache this view for an hour
    @method_decorator(cache_page(60*60))
    def get(self, request, *args, **kwargs):
        response = requests.get(
            f"https://syllabuskrk.agh.edu.pl/{kwargs.get('academic_year')}/magnesite/api/faculties/"
            f"{kwargs.get('department')}/study_plans/")
        try:
            study_types_json_data = json.loads(response.content).get('syllabus').get('study_types')
            serializer = StudyTypesSerializer(data=study_types_json_data, many=True, context={'request': request})
            if serializer.is_valid():
                return Response(serializer.data)
            else:
                return Response(serializer.errors)
        except json.JSONDecodeError:
            return Response({'Syllabus': {'content': response.content}}, status=status.HTTP_404_NOT_FOUND)


class StudyProgrammesImportView(GenericViewSet):
    """
    List of study programme's semesters, groups, modules and classes
    """
    serializer_class = ImportModulesSerializer

    # cache this view for an hour
    @method_decorator(cache_page(60*60))
    def get(self, request, *args, **kwargs):
        response = requests.get(
            f"https://syllabuskrk.agh.edu.pl/{kwargs.get('academic_year')}/magnesite/api/faculties/"
            f"{kwargs.get('department')}/study_plans/{kwargs.get('study_plan')}/")
        try:
            json_data = json.loads(response.content).get('syllabus')
            modules = []
            for semester in json_data.get('study_plan').get('semesters'):
                for group in semester.get('groups'):
                    for module in group.get('modules'):
                        modules.append(module)
            return Response(modules)
        except json.JSONDecodeError:
            return Response({'Syllabus': {'content': response.content}}, status=status.HTTP_404_NOT_FOUND)
        except TypeError:
            return Response({'error': 'No valid data to display'})

    # required by GenericViewSet with post() method
    def get_queryset(self):
        pass

    def post(self, request, *args, **kwargs):
        data = self.get(request, *args, **kwargs).data
        data = data if isinstance(data, list) else [data]
        schedule = Schedules.objects.get(slug=request.data.get('schedule'))
        for sub_data in data:
            sub_data['schedule'] = schedule
        serializer = ModuleSerializer(data=data, many=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
