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

router.register(r'classes', views.ClassViewSet)
## generates:
# /orders/
# /orders/{module_code/order's name'}

urlpatterns = [
    # unique path for retrieving one order by it's module's code and class' name - needs implementation of unique url
    # allows: /modules/{module_code}/classes/{order_name}
    path(
        'modules/<str:module_code>/classes/<str:name>/',
        views.ClassViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy',
        }),
        name='classes-detail',
    ),
    path('', include(router.urls)),
    path('', include(employees_router.urls)),
]
