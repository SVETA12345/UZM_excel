from django.urls import path, include

from . import views
from .views_api import *

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'run', RunViewSet, basename='run')
router.register(r'section', SectionViewSet, basename='section')
router.register(r'wellbore', WellboreViewSet, basename='wellbore')
router.register(r'well', WellViewSet, basename='well')
router.register(r'pad', PadViewSet, basename='pad')
router.register(r'field', FieldViewSet, basename='field')
router.register(r'well_with_run', WellWithRunViewSet, basename='wellbyrun')

urlpatterns = [
    path('add_contractor_nnb/', views.add_contractor_nnb, name='add_contractor_nnb'),
    path('add_contractor_drill/', views.add_contractor_drill, name='add_contractor_drill'),
    path('add_field/', views.add_field, name='add_field'),
    path('add_pad/', views.add_pad, name='add_pad'),
    path('add_well/', views.add_well, name='add_well'),
    path('add_wellbore/', views.add_wellbore, name='add_wellbore'),
    path('add_section/', views.add_section, name='add_section'),
    path('add_run/', views.add_run, name='add_run'),
    # path('add_client/', views.add_client, name='add_client'),
    path('api/client', ClientAPIView.as_view()),
    path('api/well_by_client/<int:client_pk>/', WellByClient.as_view()),
    path('api/section_by_well/<int:well_id>/', SectionByWell.as_view()),
    path('api/run_by_well/<int:well_id>/', RunByWell.as_view()),
    path('api/contractorNNB', ContractorNnbAPIView.as_view()),
    path('api/contractorDrill', ContractorDrillAPIView.as_view()),
    path('api/', include(router.urls)),
    path('api/get_field', get_field_by_do, name='get_field_by_do'),
    path('api/get_pad', get_pad_by_field, name='run_index'),
    path('api/wellbore/clone', views.clone_wellbore),
    path('api/well/summary', views.well_summary, name='add_summary'),
    path('api/well/igirgi_drilling', views.edit_igirgi_drilling),
]
