from django.urls import path, include

from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'degrees', views.DegreeViewSet)
router.register(r'positions', views.PositionViewSet)
router.register(r'employees', views.EmployeeViewSet)
router.register(r'modules', views.ModulesViewSet)

#app_name = 'employees'
urlpatterns = [
    path('', include(router.urls)),
    ]
