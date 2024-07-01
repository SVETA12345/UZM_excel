# Viewsets - все миксины с добавлением, удалением, редактированием, выбором
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from .models import *
from .serializer import *
from django.http import JsonResponse
from rest_framework import generics, viewsets, mixins
from rest_framework.response import Response
from rest_framework.views import APIView

from Field.models import Run, Wellbore


# class FileIndexView(APIView):
#     """ Индексы для чтения траектории ННБ/ИГиРГИ/Плановой/Динамической/Сырой"""
#     @swagger_auto_schema(tags=['Чтение файлов'],
#                          operation_summary="Получить индексы для чтения файлов с траекторие",
#                          request_body=openapi.Schema(
#                              type=openapi.TYPE_OBJECT,
#                              properties={
#                                  'run_id': openapi.Schema(type=openapi.TYPE_NUMBER, description='id рейса'),
#                              }
#                          ),
#                          responses={200: openapi.Response('response description', ReportIndexSerializer)},
#                          )
#     def post(self, request):
#         try:
#             run_id = request.POST.get('run_id')
#             if run_id != "Выберите рейс":
#                 obj = Run.objects.get(id=run_id)
#                 report_index = ReportIndex.objects.get(run=obj)
#                 return Response(ReportIndexSerializer(report_index).data)
#         except ReportIndex.DoesNotExist:
#             pass
#         except Run.DoesNotExist:
#             pass
#         return Response(ReportIndexSerializer().data)
