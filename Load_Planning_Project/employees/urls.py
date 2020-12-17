from django.urls import path, include

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'degrees', views.DegreeViewSet)
router.register(r'positions', views.PositionViewSet)
router.register(r'employees', views.EmployeeViewSet)
router.register(r'modules', views.ModulesViewSet)
router.register(r'orders', views.OrdersViewSet)

#app_name = 'employees'
urlpatterns = [
    path(
        'orders/<str:module>_<str:lesson_type>/',
        views.OrdersViewSet.as_view({
            'get': 'retrieve',
        }),
        name='orders-detail'
    ),
    path('', include(router.urls)),
    ]
