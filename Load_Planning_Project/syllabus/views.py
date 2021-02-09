import json
import requests

from django.shortcuts import redirect
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from .serializers import SyllabusSerializer, StudyTypesSerializer


class SyllabusView(GenericViewSet):
    """
    Simple form for pointing data to get from syllabus web API
    """
    serializer_class = SyllabusSerializer

    def list(self, request):
        # just to display serializer's form without http error
        return Response()

    def post(self, request):
        return redirect('syllabus-study_types-list', **{
            'academic_year': request.data['academic_year'],
            'department': request.data['department'].lower()
        })


class StudyTypesListView(APIView):
    """
    List of study programmes from Syllabus web API
    """
    def get(self, request, **kwargs):
        academic_year = kwargs.get('academic_year')
        department = kwargs.get('department')
        if academic_year and department:
            response = requests.get(
                f"https://syllabuskrk.agh.edu.pl/{academic_year}/magnesite/api/faculties/"
                f"{department.lower()}/study_plans/")
            try:
                json_data = json.loads(response.content)
                serializer = StudyTypesSerializer(data=json_data.get('syllabus').get('study_types'), many=True)
                if serializer.is_valid():
                    return Response(serializer.data)
                else:
                    return Response(serializer.errors)
            except json.JSONDecodeError:
                return Response({'Syllabus': {'content': response.content}}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'Academic year or department missing'}, status=status.HTTP_404_NOT_FOUND)
