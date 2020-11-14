from django.urls import path

from . import views

app_name = 'employees'
urlpatterns = [
    path('', views.index, name='index'),
    path('degrees', views.degrees, name='degrees'),
    path('positions', views.positions, name='positions'),
]
