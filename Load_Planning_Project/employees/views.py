from .models import Degrees, Positions
from django.shortcuts import render


def index(request):
    context = {
        'degrees': Degrees.objects.all().order_by('name'),
        'positions': Positions.objects.all().order_by('name'),
    }
    return render(request, 'employees/index.html', context)

