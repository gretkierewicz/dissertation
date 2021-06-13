from datetime import datetime, timedelta

# list taken from syllabus: https://syllabuskrk.agh.edu.pl/2019-2020/magnesite/api/faculties/WRONG_DEP_NAME/study_plans
DEPARTMENTS_LOWERCASE = 'wimir, weaiiib, wgig, wimiip, wggiis, wimic, wh, wwnig, wieit, weip, wggios, wmn, wms, wfiis, ' \
                  'wz, wo, wgtjz, wiwm'.split(', ')
DEPARTMENTS_LOWERCASE.sort()

# timedelta because academic year starts/ends with Oct (Oct as 10th month of the year - 2 months offset) * ~30.5 days
DAY_OFFSET = (10 - 2) * 30.5
# TODO: to be precise, at what month new academic year should be available to pick?
ACADEMIC_TIME_WITH_OFFSET = datetime.now() - timedelta(days=-DAY_OFFSET)
ACADEMIC_YEAR_STARTS_WITH = 2015

DEPARTMENTS = [(dep_name, dep_name.upper()) for dep_name in DEPARTMENTS_LOWERCASE]
ACADEMIC_YEARS = [
    f"{year}-{year + 1}" for year in range(ACADEMIC_YEAR_STARTS_WITH, ACADEMIC_TIME_WITH_OFFSET.year)
][::-1]

# pensum groups
BADAWCZO_DYDAKTYCZNA = 'badawczo-dydaktyczna'
DYDAKTYCZNA = 'dydaktyczna'