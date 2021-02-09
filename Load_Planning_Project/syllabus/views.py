import json
import requests

from django.shortcuts import redirect
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from .serializers import SyllabusSerializer, StudyTypesSerializer, SemestersSerializer, StudyPlanSerializer


class SyllabusView(GenericViewSet):
    """
    Simple form for pointing data to get from syllabus web API
    """
    serializer_class = SyllabusSerializer

    def list(self, request):
        # just to display serializer's form without http error
        return Response()

    def post(self, request):
        return redirect('syllabus-study_plans-list', **{
            'academic_year': request.data['academic_year'],
            'department': request.data['department']
        })


class StudyProgrammesListView(APIView):
    """
    List of study programmes from Syllabus web API
    """
    def get(self, request, **kwargs):
        response = requests.get(
            f"https://syllabuskrk.agh.edu.pl/{kwargs.get('academic_year')}/magnesite/api/faculties/"
            f"{kwargs.get('department')}/study_plans/")
        try:
            json_data = json.loads(response.content)
            serializer = StudyTypesSerializer(
                data=json_data.get('syllabus').get('study_types'),
                many=True,
                context={'request': request}
            )
            if serializer.is_valid():
                return Response(serializer.data)
            else:
                return Response(serializer.errors)
        except json.JSONDecodeError:
            return Response({'Syllabus': {'content': response.content}}, status=status.HTTP_404_NOT_FOUND)


class StudyProgrammesInstanceView(APIView):
    def get(self, request, **kwargs):
        response = requests.get(f"https://syllabuskrk.agh.edu.pl/{kwargs.get('academic_year')}/magnesite/api/faculties"
                                f"/{kwargs.get('department')}/study_plans/{kwargs.get('study_plan')}/")
        try:
            json_data = json.loads(response.content)
            serializer = StudyPlanSerializer(data=json_data.get('syllabus').get('study_plan'))
            if serializer.is_valid():
                return Response(serializer.data)
            else:
                return Response(serializer.errors)
        except json.JSONDecodeError:
            return Response({'Syllabus': {'content': response.content}}, status=status.HTTP_404_NOT_FOUND)
