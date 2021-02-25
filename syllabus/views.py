import json
import requests

from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from .serializers import SyllabusSerializer, StudyTypesSerializer, ProgrammeSerializer, get_name_from_slug


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


class StudyProgrammesDetailView(APIView):
    """
    List of study programme's semesters, groups, modules and classes
    """
    # cache this view for an hour
    @method_decorator(cache_page(60*60))
    def get(self, request, *args, **kwargs):
        response = requests.get(
            f"https://syllabuskrk.agh.edu.pl/{kwargs.get('academic_year')}/magnesite/api/faculties/"
            f"{kwargs.get('department')}/study_plans/{kwargs.get('study_plan')}/")
        try:
            json_data = json.loads(response.content).get('syllabus')
            json_data['study_plan'].update({'name': get_name_from_slug(kwargs.get('study_plan'))})
            serializer = ProgrammeSerializer(data=json_data)
            if serializer.is_valid():
                return Response(serializer.data)
            else:
                return Response(serializer.errors)
        except json.JSONDecodeError:
            return Response({'Syllabus': {'content': response.content}}, status=status.HTTP_404_NOT_FOUND)
