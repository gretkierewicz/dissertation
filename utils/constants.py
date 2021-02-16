from datetime import datetime, timedelta

# list taken from syllabus: https://syllabuskrk.agh.edu.pl/2019-2020/magnesite/api/faculties/WRONG_DEP_NAME/study_plans
low_departments = 'wimir, weaiiib, wgig, wimiip, wggiis, wimic, wh, wwnig, wieit, weip, wggios, wmn, wms, wfiis, ' \
                  'wz, wo, wgtjz, wiwm'.split(', ')
low_departments.sort()

# timedelta because academic year starts/ends with Oct (Oct as 10th month of the year - 2 months offset) * ~30.5 days
day_offset = (10 - 2) * 30.5
# TODO: to be precise, at what month new academic year should be available to pick?
academic_time_with_offset = datetime.now() - timedelta(days=-day_offset)
academic_year_start_with = 2015

GT = 'greater than'
ET = 'equal to'
LT = 'less than'
NA = 'N/A'

DEPARTMENTS = [(_, _.upper()) for _ in low_departments]
ACADEMIC_YEARS = [f"{_}-{_ + 1}" for _ in range(academic_year_start_with, academic_time_with_offset.year)][::-1]
