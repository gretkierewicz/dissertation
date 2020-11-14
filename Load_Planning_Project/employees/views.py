from .models import Degrees, Positions
from django.shortcuts import render


def index(request):
    context = {
        'table_name': 'Employees',
    }
    return render(request, 'employees/index.html', context)


def degrees(request):
    context = {
        'table_name': 'Degrees',
        'objects': Degrees.objects.all().order_by('name'),
    }
    return render(request, 'employees/index.html', context)


def positions(request):
    context = {
        'table_name': 'Positions',
        'objects': Positions.objects.all().order_by('name'),
    }
    return render(request, 'employees/index.html', context)
