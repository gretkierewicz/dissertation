from django.contrib import admin

from .models import ExamsAdditionalHours, Pensum, PensumAdditionalHoursFactors, PensumBasicThresholdFactors, \
    PensumReductions, Schedules

admin.site.register(Schedules)
admin.site.register(Pensum)
admin.site.register(PensumReductions)
admin.site.register(PensumBasicThresholdFactors)
admin.site.register(PensumAdditionalHoursFactors)
admin.site.register(ExamsAdditionalHours)
