from django.contrib import admin

from .models import Degrees, Employees, Positions

admin.site.register(Degrees)
admin.site.register(Positions)
admin.site.register(Employees)
