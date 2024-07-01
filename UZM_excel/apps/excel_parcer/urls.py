from django.urls import path, include

from . import views, views_api
from .views_api import *
from rest_framework import routers


urlpatterns = [
    # API для внешних запросов
    path('api/telesystem', DeviceListView.as_view({'get': 'list'})),
    path('api/telesystem/<int:run_id>', DeviceCoefApiView.as_view()),
    path('api/meas/run/<int:run_id>/', DataByRunAPIView.as_view()),
    path('api/meas/<int:pk>/', DataViewSet.as_view({'get': 'retrieve', 'post': 'create', 'put': 'update',
                                                    'delete': 'destroy'})),
    path('api/raw_meas/run/<int:run_id>/', RawDataByRunAPIView.as_view()),

    # Отрисовка шаблонов (клиент)
    path('', views.index, name='axes'),
    path('graph', views.graph, name='graph_axes'),
    path('settings', views.settings, name="axes-settings"),
    path('edit', views.edit_index, name='edit_axes'),
    path('telesystem', views.add_Device, name='add_device'),

    # API для собственных fetch запросов
    path('run_index', views.get_run_index, name='run_index'),
    path('api/device_del', views.del_Device, name='device_del'),
    path('api/meas_del', views.del_Meas, name='meas_del'),
    path('api/coef_device', views.get_coef_device, name='device_coef'),
    path('api/upload_file', views.uploadAxesFile),
    path('api/comm', views.axes_comm),
    path('api/wellbore_copy', wellbore_copy),
    path('api/addAxes', add_Axes),
    path('api/updateAxes', update_Axes),
]
