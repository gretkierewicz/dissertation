import re

from rest_framework.fields import ChoiceField, CharField, SerializerMethodField
from rest_framework.serializers import Serializer

from utils.constants import ACADEMIC_YEARS, DEPARTMENTS


class ProgrammesSerializer(Serializer):
    name_from_slug = SerializerMethodField()
    syllabus_url = CharField()
    slug = SerializerMethodField()

    def to_internal_value(self, data):
        url = data.pop('url')
        data['syllabus_url'] = url
        return data

    def get_name_from_slug(self, data):
        slug = self.get_slug(data)
        if slug:
            search = re.search(r'(stacjonarne-)*(niestacjonarne-)*(?P<name>[a-z-]+[a-z])-*(?P<number>[\d]*)', slug)
            words = search.group('name').split(sep='-')
            if search.group('number'):
                words.append(f"({search.group('number')})")
            name = ' '.join(words)
            return name.capitalize()
        return ''

    def get_slug(self, data):
        url = data.get('syllabus_url')
        if url:
            slug = re.search(
                r'/study_plans/(?P<name>[\w-]+)', url).group('name')
            return slug
        return ''


class LevelsSerializer(Serializer):
    level = CharField()
    code = CharField()
    study_programmes = ProgrammesSerializer(many=True)


class StudyTypesSerializer(Serializer):
    type = CharField()
    code = CharField()
    levels = LevelsSerializer(many=True)


class SyllabusSerializer(Serializer):
    department = ChoiceField(choices=DEPARTMENTS, required=False)
    academic_year = ChoiceField(choices=ACADEMIC_YEARS, required=False)
