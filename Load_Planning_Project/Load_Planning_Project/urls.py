"""Load_Planning_Project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path

from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter

from . import views
from employees import views as employees_views
from modules import views as modules_views
from orders import views as orders_views

router = DefaultRouter()
router.register(r'degrees', employees_views.DegreeViewSet)
# generates:
# /degrees/
# /degrees/{position_pk}

router.register(r'positions', employees_views.PositionViewSet)
# generates:
# /positions/
# /positions/{position_pk}

router.register(r'pensum', employees_views.PensumViewSet)
# generates
# /pensum/
# /pensum/{pensum_pk}

router.register(r'employees', employees_views.EmployeeViewSet)
# generates:
# /employees/
# /employees/{employee_abbreviation}
employees_router = NestedDefaultRouter(router, r'employees', lookup='employee')
employees_router.register(r'modules', modules_views.EmployeeModuleViewSet, basename='employee-modules')
# generates:
# /employees/{employee_abbreviation}/modules/
# /employees/{employee_abbreviation}/modules/{module_code}/

router.register(r'modules', modules_views.ModuleViewSet)
# generates:
# /modules/
# /modules/{module_code}
modules_router = NestedDefaultRouter(router, r'modules', lookup='module')
modules_router.register(r'classes', modules_views.ClassViewSet, basename='classes')
# generates:
# /modules/{module_code}/classes/
# /modules/{module_code}/classes/{classes_name}
order_plans_router = NestedDefaultRouter(modules_router, r'classes', lookup='classes')
order_plans_router.register(r'order/plans', orders_views.PlansViewSet, basename='classes-order-plans')
# gernerates:
# /modules/{module_code}/classes/{classes_name}/order/plans/
# /modules/{module_code}/classes/{classes_name}/order/plans/{plans_employee}

router.register(r'orders', orders_views.OrdersListViewSet, basename='orders')
# generates:
# /orders/

urlpatterns = [
    path('API/', include(router.urls)),
    path('API/', include([re_path(
        r'^modules/(?P<module_module_code>[^/.]+)/classes/(?P<classes_name>[^/.]+)/order/$',
        orders_views.OrderDetailViewSet.as_view({
            # request's method name relation with ViewSet's method name (custom create_or_update method)
            'get': 'retrieve',
            'put': 'create_or_update',
            'patch': 'partial_update',
            'delete': 'destroy'
        }),
        name='classes-order-detail')])),
    path('API/', include([re_path(
        r'^modules/(?P<module_module_code>[^/.]+)/classes/(?P<classes_name>[^/.]+)/order\.(?P<format>[a-z0-9]+)/?$',
        orders_views.OrderDetailViewSet.as_view({
            'get': 'retrieve',
            'put': 'create_or_update',
            'patch': 'partial_update',
            'delete': 'destroy'
        }),
        name='classes-order-detail')])),
    path('API/', include(order_plans_router.urls)),
    path('API/', include(employees_router.urls)),
    path('API/', include(modules_router.urls)),
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
]
