from django.urls import path, include

from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter

from . import views

router = DefaultRouter()
router.register(r'degrees', views.DegreeViewSet)
router.register(r'positions', views.PositionViewSet)
router.register(r'employees', views.EmployeeViewSet)
router.register(r'modules', views.ModuleViewSet)
router.register(r'orders', views.OrderViewSet)

employees_router = NestedDefaultRouter(router, r'employees', lookup='employee')
employees_router.register(r'modules', views.EmployeeModuleViewSet, basename='employee-modules')
## generates:
# /employees/{employee_abbreviation}/modules/
# /employees/{employee_abbreviation}/modules/{module_code}/

#app_name = 'employees'
urlpatterns = [
    path(
        'orders/<str:module>_<str:lesson_type>/',
        views.OrderViewSet.as_view({
            'get': 'retrieve',
        }),
        name='orders-detail'
    ),
    path('', include(router.urls)),
    path('', include(employees_router.urls)),
    ]
