from django.urls import path, include

from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter

from . import views

router = DefaultRouter()
router.register(r'degrees', views.DegreeViewSet)
## generates:
# /degrees/
# /degrees/{position_pk}

router.register(r'positions', views.PositionViewSet)
## generates:
# /positions/
# /positions/{position_pk}

router.register(r'pensum', views.PensumViewSet)
## generates
# /pensum/
# /pensum/{pensum_pk}

router.register(r'employees', views.EmployeeViewSet)
## generates:
# /employees/
# /employees/{employee_abbreviation}
employees_router = NestedDefaultRouter(router, r'employees', lookup='employee')
employees_router.register(r'modules', views.EmployeeModuleViewSet, basename='employee-modules')
## generates:
# /employees/{employee_abbreviation}/modules/
# /employees/{employee_abbreviation}/modules/{module_code}/

router.register(r'modules', views.ModuleViewSet)
## generates:
# /modules/
# /modules/{module_code}
modules_router = NestedDefaultRouter(router, r'modules', lookup='module')
modules_router.register(r'classes', views.ClassViewSet, basename='classes')
## generates:
# /modules/{module_code}/classes/
# /modules/{module_code}/classes/{class_name}
classes_router = NestedDefaultRouter(modules_router, r'classes', lookup='class')
classes_router.register(r'plans', views.PlanViewSet, basename='plans')
## generates:
# /modules/{module_code}/classes/{class_name}/plans/
# /modules/{module_code}/classes/{class_name}/plans/{employee}

urlpatterns = [
    path('', include(router.urls)),
    path('', include(employees_router.urls)),
    path('', include(modules_router.urls)),
    path('', include(classes_router.urls)),
]
