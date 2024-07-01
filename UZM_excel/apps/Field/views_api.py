from typing import Dict

from django.db.models import QuerySet
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, viewsets, mixins
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.utils.serializer_helpers import ReturnDict
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from .models import *
from .serializer import *
from .serializerTree import Tree


class ClientAPIView(APIView):
    @swagger_auto_schema(tags=['ДО'],
                         operation_summary="Получить все дочерние общества")
    def get(self, request):
        clients = Client.objects.all()
        for c in clients:
            c.full_name = str(c)
        return Response(ClientSerializer(clients, many=True).data)

    # def post(self, request):
    #     serializers = ClientSerializer(data=request.data)
    #     serializers.is_valid(raise_exception=True)
    #     serializers.save()
    #     return Response({'post': serializers.data})


class WellByClient(APIView):
    """Получаем список скважин по id заказчика"""

    @swagger_auto_schema(tags=['Скважина'],
                         operation_summary="Получить список скважин по id клиента")
    def get(self, request, client_pk):
        wells = Well.objects.filter(pad_name__field__client__id=client_pk)
        return Response(WellSerializer(wells, many=True).data)


class RunByWell(APIView):
    """Получаем список рейсов по id скважины"""

    @swagger_auto_schema(tags=['Рейс'],
                         operation_summary="Получить список рейсов по id скважины")
    def get(self, request, well_id):
        runs = Run.objects.filter(section__wellbore__well_name__id=well_id)
        return Response(RunSerializer(runs, many=True).data)


class SectionByWell(APIView):
    """Получаем список секций по id скважины"""

    @swagger_auto_schema(tags=['Секция'],
                         operation_summary="Получить все секции по id скважины")
    def get(self, request, well_id):
        sections = Section.objects.filter(wellbore__well_name__id=well_id)
        return Response(SectionSerializer(sections, many=True).data)


@method_decorator(name='post',
                  decorator=swagger_auto_schema(tags=['Подрядчик по ННБ'],
                                                operation_summary="Добавить подрядчика ННБ"))
@method_decorator(name='get',
                  decorator=swagger_auto_schema(tags=['Подрядчик по ННБ'],
                                                operation_summary="Получить всех подрядчиков по ННБ"))
class ContractorNnbAPIView(generics.ListCreateAPIView):
    queryset = ContractorNNB.objects.all()
    serializer_class = ContractorNNBSerializer


@method_decorator(name='post',
                  decorator=swagger_auto_schema(tags=['Подрядчик по бурению'],
                                                operation_summary="Добавить подрядчика по бурению"))
@method_decorator(name='get',
                  decorator=swagger_auto_schema(tags=['Подрядчик по бурению'],
                                                operation_summary="Получить всех подрядчиков по бурению"))
class ContractorDrillAPIView(generics.ListCreateAPIView):
    queryset = ContractorDrill.objects.all()
    serializer_class = ContractorDrillSerializer


class FieldApiView(generics.ListAPIView):
    queryset = Field.objects.all()
    serializer_class = FieldSerializer


class PadApiView(generics.ListCreateAPIView):
    queryset = Pad.objects.all()
    serializer_class = PadSerializer


# Viewsets - все миксины с добавлением, удалением, редактированием, выбором
@method_decorator(name='create',
                  decorator=swagger_auto_schema(tags=['Рейс'], operation_summary="Добавить рейс"))
@method_decorator(name='update',
                  decorator=swagger_auto_schema(tags=['Рейс'], operation_summary="Обновить данные рейса по id"))
@method_decorator(name='destroy',
                  decorator=swagger_auto_schema(tags=['Рейс'], operation_summary="Удалить данные рейса по id"))
@method_decorator(name='retrieve',
                  decorator=swagger_auto_schema(tags=['Рейс'], operation_summary="Получить данные рейса по id"))
@method_decorator(name='list',
                  decorator=swagger_auto_schema(tags=['Рейс'], operation_summary="Получить все рейсы"))
class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.all()
    serializer_class = RunSerializer


@method_decorator(name='create',
                  decorator=swagger_auto_schema(tags=['Секция'], operation_summary="Добавить секцию"))
@method_decorator(name='update',
                  decorator=swagger_auto_schema(tags=['Секция'], operation_summary="Обновить данные секции по id"))
@method_decorator(name='destroy',
                  decorator=swagger_auto_schema(tags=['Секция'], operation_summary="Удалить данные секции по id"))
@method_decorator(name='retrieve',
                  decorator=swagger_auto_schema(tags=['Секция'], operation_summary="Получить данные секции по id"))
@method_decorator(name='list',
                  decorator=swagger_auto_schema(tags=['Секция'], operation_summary="Получить все секции"))
class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer


@method_decorator(name='create',
                  decorator=swagger_auto_schema(tags=['Ствол'], operation_summary="Добавить ствол"))
@method_decorator(name='update',
                  decorator=swagger_auto_schema(tags=['Ствол'], operation_summary="Обновить данные ствола по id"))
@method_decorator(name='destroy',
                  decorator=swagger_auto_schema(tags=['Ствол'], operation_summary="Удалить данные ствола по id"))
@method_decorator(name='retrieve',
                  decorator=swagger_auto_schema(tags=['Ствол'], operation_summary="Получить данные ствола по id"))
@method_decorator(name='list',
                  decorator=swagger_auto_schema(tags=['Ствол'], operation_summary="Получить все стволы"))
class WellboreViewSet(viewsets.ModelViewSet):
    queryset = Wellbore.objects.all()
    serializer_class = WellboreSerializer
    permission_classes = [AllowAny]


@method_decorator(name='create',
                  decorator=swagger_auto_schema(tags=['Скважина'], operation_summary="Добавить скважину"))
@method_decorator(name='update',
                  decorator=swagger_auto_schema(tags=['Скважина'], operation_summary="Обновить данные скважины по id"))
@method_decorator(name='destroy',
                  decorator=swagger_auto_schema(tags=['Скважина'], operation_summary="Удалить данные скважины по id"))
@method_decorator(name='retrieve',
                  decorator=swagger_auto_schema(tags=['Скважина'], operation_summary="Получить данные скважины по id"))
@method_decorator(name='list',
                  decorator=swagger_auto_schema(tags=['Скважина'], operation_summary="Получить все скважины"))
class WellViewSet(viewsets.ModelViewSet):
    queryset = Well.objects.all()
    serializer_class = WellSerializer


@method_decorator(name='create',
                  decorator=swagger_auto_schema(tags=['Куст'], operation_summary="Добавить куст"))
@method_decorator(name='update',
                  decorator=swagger_auto_schema(tags=['Куст'], operation_summary="Обновить данные куста по id"))
@method_decorator(name='destroy',
                  decorator=swagger_auto_schema(tags=['Куст'], operation_summary="Удалить данные куста по id"))
@method_decorator(name='retrieve',
                  decorator=swagger_auto_schema(tags=['Куст'], operation_summary="Получить данные куста по id"))
@method_decorator(name='list',
                  decorator=swagger_auto_schema(tags=['Куст'], operation_summary="Получить все кусты"))
class PadViewSet(viewsets.ModelViewSet):
    queryset = Pad.objects.all()
    serializer_class = PadSerializer


@method_decorator(name='create',
                  decorator=swagger_auto_schema(tags=['Месторождение'], operation_summary="Добавить месторождение"))
@method_decorator(name='update',
                  decorator=swagger_auto_schema(tags=['Месторождение'], operation_summary="Обновить данные "
                                                                                          "месторождение по id"))
@method_decorator(name='destroy',
                  decorator=swagger_auto_schema(tags=['Месторождение'], operation_summary="Удалить данные "
                                                                                          "месторождение по id"))
@method_decorator(name='retrieve',
                  decorator=swagger_auto_schema(tags=['Месторождение'], operation_summary="Получить данные "
                                                                                          "месторождение по id"))
@method_decorator(name='list',
                  decorator=swagger_auto_schema(tags=['Месторождение'], operation_summary="Получить все месторождения"))
class FieldViewSet(viewsets.ModelViewSet):
    queryset = Field.objects.all()
    serializer_class = FieldSerializer


@method_decorator(name='retrieve',
                  decorator=swagger_auto_schema(tags=['Скважина'], operation_summary="Получить скважину и все модели"
                                                                                     " по id"))
@method_decorator(name='list',
                  decorator=swagger_auto_schema(tags=['Скважина'], operation_summary="Получить скважину и все модели"))
class WellWithRunViewSet(mixins.RetrieveModelMixin,
                         mixins.ListModelMixin,
                         GenericViewSet):
    """
    Явная связь скважина-ствол-секция-рейс
    """
    queryset = Well.objects.all()
    serializer_class = WellWithRunSerializer


def get_tree() -> dict[str, QuerySet]:
    """ Дерево для меню [Здесь лежит дерево на сериализаторах и все рейсы для поиска]"""
    trees = Tree(Client.objects.all().prefetch_related('fields__pads__wells__wellbores__sections__runs'), many=True).data
    runs = Run.objects.all().order_by('-id').select_related('section__wellbore__well_name__pad_name__field__client')
    return {'main': trees, 'search': runs}


# смежные api
def get_field_by_do(request):
    """Функция для фильтрации"""
    field_data = dict()
    for field in Field.objects.filter(client=request.POST.get("do_id")):
        field_data[field.id] = field.field_name
    return JsonResponse(field_data)


def get_pad_by_field(request):
    """Функция для фильтрации"""
    pad_data = dict()
    for pad in Pad.objects.filter(field=request.POST.get("field_id")):
        pad_data[pad.id] = pad.pad_name
    return JsonResponse(pad_data)
