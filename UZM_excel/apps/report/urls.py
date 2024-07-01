from django.urls import path

from . import views
from .views_api import *

# Точки для работы с моделями траектории [обращаемся с DjangoTemplate по fetch запросу]
urlpatterns = [
    path('api/run_index', views.run_index, name='run_index'),
    path('api/update_index', views.update_index),
    path('api/file_name', views.report, name='get_file_name'),
    path('api/get_file', views.get_report_file, name='get_report_file'),
    path('api/final_report', views.get_final_report),
    path('api/att_final_report', views.get_attachments_final_report),
    path('api/plan_del', views.plan_del, name='plan_del'),
    path('api/wellbore_copy', views.wellbore_copy, name='clone'),
    path('api/meas_del', views.traj_del, name='traj_del'),
    path('api/traj_comm', views.put_comment),
    path('api/upload_file', views.uploadFile),  # внутри смотрим на то какой файл нам пришел
    # масштаб графиков!
    path('api/projection_param/<int:wellbore_id>', views.proj_param),
    path('api/quality_graph_param/<int:wellbore_id>', views.quality_param, name='quality_param'),
]
