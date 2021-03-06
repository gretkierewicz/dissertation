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
from django.urls import include, path, re_path
from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter

from employees import views as employees_views
from modules import views as modules_views
from orders import views as orders_views
from schedules import views as schedules_views
from syllabus import views as syllabus_views
from . import views

router = DefaultRouter()
router.register(r'degrees', employees_views.DegreeViewSet)
# generates:
# /degrees/
# /degrees/{pk}
router.register(r'positions', employees_views.PositionViewSet)
# generates:
# /positions/
# /positions/{pk}
router.register(r'employees', employees_views.EmployeeViewSet)
# generates:
# /employees/
# /employees/{abbreviation}

router.register(r'schedules', schedules_views.SchedulesViewSet, basename='schedules')
# generates:
# /schedules/
# /schedules/{slug}
schedules_router = NestedDefaultRouter(router, r'schedules', lookup='schedule')
schedules_router.register(r'modules', modules_views.ModuleViewSet, basename='modules')
# generates:
# /schedules/{schedule_slug}/modules/
# /schedules/{schedule_slug}/modules/{module_code}
modules_router = NestedDefaultRouter(schedules_router, r'modules', lookup='module')
modules_router.register(r'classes', modules_views.ClassViewSet, basename='classes')
# generates:
# /schedules/{schedule_slug}/modules/{module_module_code}/classes/
# /schedules/{schedule_slug}/modules/{module_module_code}/classes/{name}
classes_order_paths = [
    re_path(r'^schedules/(?P<schedule_slug>[^/.]+)/modules/'
            r'(?P<module_module_code>[^/.]+)/classes/'
            r'(?P<classes_name>[^/.]+)/order/$',
            orders_views.OrderDetailViewSet.as_view({
                # request's method name relation with ViewSet's
                # method name (custom create_or_update method)
                'get': 'retrieve',
                'put': 'create_or_update',
                'patch': 'partial_update',
                'delete': 'destroy'
            }),
            name='classes-order-detail')]
# generates:
# /schedules/{schedule_slug}/modules/{module_module_code}/classes/{classes_name}/order/
order_plans_router = NestedDefaultRouter(modules_router, r'classes', lookup='classes')
order_plans_router.register(r'order/plans', orders_views.PlansViewSet, basename='classes-order-plans')
# generates:
# /schedules/{schedule_slug}/modules/{module_module_code}/classes/{classes_name}/order/plans/
# /schedules/{schedule_slug}/modules/{module_module_code}/classes/{classes_name}/order/plans/{employee}
schedules_router.register(r'orders', orders_views.OrdersViewSet, basename='orders')
# generates:
# /schedules/{schedule_slug}/orders/
schedules_router.register(r'pensums', schedules_views.PensumViewSet, basename='pensums')
# generates:
# /schedules/{schedule_slug}/pensum/
# /schedules/{schedule_slug}/pensum/{employee}
pensum_router = NestedDefaultRouter(schedules_router, r'pensums', lookup='pensums')
pensum_reduction_paths = [
    re_path(r'^schedules/(?P<schedule_slug>[^/.]+)/pensums/(?P<pensums_employee>[^/.]+)/reduction/$',
            schedules_views.PensumReductionViewSet.as_view({
                # request's method name relation with ViewSet's method name (custom create_or_update method)
                'get': 'retrieve',
                'put': 'create_or_update',
                'patch': 'partial_update',
                'delete': 'destroy'
            }), name='pensum-reduction-detail')]
# /schedules/{schedule_slug}/pensum/{pensums_employee}/reduction/
pensum_router.register(r'factors', schedules_views.PensumBasicThresholdFactorsViewSet, basename='pensum-factors')
# generates:
# /schedules/{schedule_slug}/pensum/{pensums_employee}/factors/
# /schedules/{schedule_slug}/pensum/{pensums_employee}/factors/{pk}
pensum_router.register(
    r'additional_hours_factors',
    schedules_views.PensumAdditionalHoursFactorsViewSet,
    basename='pensum-additional_hours_factors')
# generates:
# /schedules/{schedule_slug}/pensum/{pensums_employee}/additional_hours_factors/
# /schedules/{schedule_slug}/pensum/{pensums_employee}/additional_hours_factors/{pk}
pensum_router.register(
    r'exams_additional_hours',
    schedules_views.ExamsAdditionalHoursViewSet,
    basename='pensum-exams_additional_hours')
# generates:
# /schedules/{schedule_slug}/pensum/{pensums_employee}/exams_additional_hours/
# /schedules/{schedule_slug}/pensum/{pensums_employee}/exams_additional_hours/{pk}

router.register(r'syllabus', syllabus_views.SyllabusView, basename='syllabus')
# generates:
# /syllabus/
syllabus_paths = [
    re_path(r'^syllabus/academic_year/(?P<academic_year>[^/.]+)/department/(?P<department>[^/.]+)/study_plans/$',
            syllabus_views.StudyProgrammesListView.as_view(),
            name='syllabus-study_plans-list'),
    re_path(r'^syllabus/academic_year/(?P<academic_year>[^/.]+)/department/(?P<department>[^/.]+)/study_plans/'
            r'(?P<study_plan>[^/.]+)/$',
            syllabus_views.StudyProgrammesImportView.as_view({'get': 'get', 'post': 'post'}),
            name='syllabus-study_plans-detail')]
# /syllabus/academic_year/{academic_year}/department/{department}/study_plans/
# /syllabus/academic_year/{academic_year}/department/{department}/study_plans/{study_plan}

urlpatterns = [
    path('API/', include(router.urls)),
    path('API/', include(schedules_router.urls)),
    path('API/', include(pensum_router.urls)),
    path('API/', include(pensum_reduction_paths)),
    path('API/', include(modules_router.urls)),
    path('API/', include(classes_order_paths)),
    path('API/', include(order_plans_router.urls)),
    path('API/', include(syllabus_paths)),
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
]
