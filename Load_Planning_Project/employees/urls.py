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

router.register(r'orders', views.OrderViewSet)
## generates:
# /orders/
# /orders/{module_code_order_lesson_type}

urlpatterns = [
    # unique path for retrieving one order by it's module's code and order's lesson type
    path(
        'orders/<str:module_code>_<str:lesson_type>/',
        views.OrderViewSet.as_view({
            'get': 'retrieve',
        }),
        name='orders-detail',
    ),
    path('', include(router.urls)),
    path('', include(employees_router.urls)),
    ]
