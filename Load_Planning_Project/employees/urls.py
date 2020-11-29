from django.urls import path, include

from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'degrees', views.DegreeViewSet)

app_name = 'employees'
urlpatterns = [
    path('REST_API', include(router.urls), name='REST_API'),
    path('', views.show_table, name='show_table'),
    path('<str:table_name>/show', views.show_table, name='show_table'),
    path('<str:table_name>/new', views.new_record, name='new_record'),
    path('<str:table_name>/<int:object_id>/edit', views.edit_record, name='edit_record'),
    path('<str:table_name>/<int:object_id>/del', views.del_record, name='del_record'),
    path('<str:table_name>/export', views.export_csv, name='export_csv'),
    path('<str:table_name>/import', views.import_csv, name='import_csv'),
]
