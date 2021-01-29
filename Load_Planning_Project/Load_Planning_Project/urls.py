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
from django.urls import path, include

from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter

from . import views
from employees import views as employees_views
from modules import views as modules_views
from orders import views as orders_views

router = DefaultRouter()
router.register(r'degrees', employees_views.DegreeViewSet)
## generates:
# /degrees/
# /degrees/{position_pk}

router.register(r'positions', employees_views.PositionViewSet)
## generates:
# /positions/
# /positions/{position_pk}

router.register(r'pensum', employees_views.PensumViewSet)
## generates
# /pensum/
# /pensum/{pensum_pk}

router.register(r'employees', employees_views.EmployeeViewSet)
## generates:
# /employees/
# /employees/{employee_abbreviation}
employees_router = NestedDefaultRouter(router, r'employees', lookup='employee')
employees_router.register(r'modules', modules_views.EmployeeModuleViewSet, basename='employee-modules')
## generates:
# /employees/{employee_abbreviation}/modules/
# /employees/{employee_abbreviation}/modules/{module_code}/

router.register(r'modules', modules_views.ModuleViewSet)
## generates:
# /modules/
# /modules/{module_code}
modules_router = NestedDefaultRouter(router, r'modules', lookup='module')
modules_router.register(r'classes', modules_views.ClassViewSet, basename='classes')
## generates:
# /modules/{module_code}/classes/
# /modules/{module_code}/classes/{class_name}
classes_router = NestedDefaultRouter(modules_router, r'classes', lookup='class')
classes_router.register(r'order', orders_views.OrdersViewSet, basename='class-order')
## generates:
# /modules/{module_code}/classes/{class_name}/order/
# /modules/{module_code}/classes/{class_name}/order/{order_pk}
classes_order_router = NestedDefaultRouter(classes_router, r'order', lookup='order')
classes_order_router.register(r'plans', orders_views.OrderPlansViewSet, basename='class-order-plans')

router.register(r'orders', orders_views.OrdersViewSet, basename='orders')
## generates:
# /orders/
# /orders/{order_pk} - overwritten by classes_router
orders_router = NestedDefaultRouter(router, r'orders', lookup='order')
orders_router.register(r'plans', orders_views.OrderPlansViewSet, basename='order-plans')
## generates:
# /orders/{order_pk}/plans/
# /orders/{order_pk}/plans/{plan_employee}

urlpatterns = [
    path('API/', include(router.urls)),
    path('API/', include(employees_router.urls)),
    path('API/', include(modules_router.urls)),
    path('API/', include(classes_router.urls)),
    path('API/', include(classes_order_router.urls)),
    path('API/', include(orders_router.urls)),
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
]
