import json
import requests

from django.shortcuts import redirect
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
    def get(self, request, *args, **kwargs):
        # TODO: Check if turning 'verify' param on is possible (problems with production setup)
        response = requests.get(
            f"https://syllabuskrk.agh.edu.pl/{kwargs.get('academic_year')}/magnesite/api/faculties/"
            f"{kwargs.get('department')}/study_plans/", verify=False)
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
    def get(self, request, *args, **kwargs):
        # TODO: Check if turning 'verify' param on is possible (problems with production setup)
        response = requests.get(
            f"https://syllabuskrk.agh.edu.pl/{kwargs.get('academic_year')}/magnesite/api/faculties/"
            f"{kwargs.get('department')}/study_plans/{kwargs.get('study_plan')}/",
            verify=False
        )
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
