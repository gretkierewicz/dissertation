from django.conf.urls import url
from django.urls import path, include

from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'degrees', views.DegreeViewSet)
router.register(r'positions', views.PositionViewSet)
router.register(r'employees', views.EmployeeViewSet)
router.register(r'modules', views.ModulesViewSet)
router.register(r'orders', views.OrdersViewSet)

#app_name = 'employees'
urlpatterns = [
    url(
        r'^orders/(?P<module>.+)_(?P<lesson_type>.+$)',
        views.OrdersViewSet.as_view({
            'get': 'retrieve',
        }),
        name='orders-detail'
    ),
    path('', include(router.urls)),
    ]
