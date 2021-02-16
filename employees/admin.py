from django.contrib import admin

from .models import Degrees, Positions, Employees

admin.site.register(Degrees)
admin.site.register(Positions)
admin.site.register(Employees)
