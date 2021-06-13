import re

from django.urls import reverse
from rest_framework.fields import CharField, ChoiceField, SerializerMethodField
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import Serializer

from AGH.data.constants import ACADEMIC_YEARS, DEPARTMENTS
from schedules.models import Schedules


def get_name_from_slug(slug):
    if slug:
        search = re.search(r'(stacjonarne-)*(niestacjonarne-)*(?P<name>[a-z-]+[a-z])-*(?P<number>[\d]*)', slug)
        words = search.group('name').split(sep='-')
        if search.group('number'):
            words.append(f"({search.group('number')})")
        name = ' '.join(words)
        return name.capitalize()
    return None


# STUDY TYPES SECTION
class ProgrammesSerializer(Serializer):
    name_from_slug = SerializerMethodField()
    syllabus_url = CharField()
    slug = SerializerMethodField()
    study_programmes_detail_url = SerializerMethodField(required=False)

    def to_internal_value(self, data):
        url = data.pop('url')
        data['syllabus_url'] = url
        return data

    def get_name_from_slug(self, data):
        slug = self.get_slug(data)
        return get_name_from_slug(slug)

    def get_slug(self, data):
        url = data.get('syllabus_url')
        if url:
            slug = re.search(
                r'/study_plans/(?P<name>[\w-]+)', url).group('name')
            return slug
        return ''

    def get_study_programmes_detail_url(self, data):
        kwargs = self.context.get('request').resolver_match.kwargs
        kwargs['study_plan'] = self.get_slug(data)
        return self.context.get('request').build_absolute_uri(reverse('syllabus-study_plans-detail', kwargs=kwargs))


class LevelsSerializer(Serializer):
    level = CharField()
    code = CharField()
    study_programmes = ProgrammesSerializer(many=True, required=False)


class StudyTypesSerializer(Serializer):
    type = CharField()
    code = CharField()
    levels = LevelsSerializer(many=True, required=False)


class SyllabusSerializer(Serializer):
    department = ChoiceField(choices=DEPARTMENTS, required=False)
    academic_year = ChoiceField(choices=ACADEMIC_YEARS, required=False)


# STUDY PLANS SECTION
class ImportModulesSerializer(Serializer):
    schedule = SlugRelatedField(queryset=Schedules.objects.all(), slug_field='slug')
