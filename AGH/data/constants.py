from datetime import datetime, timedelta

# list taken from syllabus: https://syllabuskrk.agh.edu.pl/2019-2020/magnesite/api/faculties/WRONG_DEP_NAME/study_plans
DEPARTMENTS_LOWERCASE = 'wimir, weaiiib, wgig, wimiip, wggiis, wimic, wh, wwnig, wieit, weip, wggios, wmn, wms, wfiis, ' \
                  'wz, wo, wgtjz, wiwm'.split(', ')
DEPARTMENTS_LOWERCASE.sort()

ACADEMIC_YEAR_ENDS_WITH = 2030
ACADEMIC_YEAR_STARTS_WITH = 2015

DEPARTMENTS = [(dep_name, dep_name.upper()) for dep_name in DEPARTMENTS_LOWERCASE]
ACADEMIC_YEARS = [
    f"{year}-{year + 1}" for year in range(ACADEMIC_YEAR_STARTS_WITH, ACADEMIC_YEAR_ENDS_WITH)
]

# pensum groups
BADAWCZO_DYDAKTYCZNA = 'badawczo-dydaktyczna'
DYDAKTYCZNA = 'dydaktyczna'