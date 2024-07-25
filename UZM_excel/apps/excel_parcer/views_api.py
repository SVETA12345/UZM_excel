# Viewsets - все миксины с добавлением, удалением, редактированием, выбором
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action

from .function.functions import new_measurements, write_to_bd, convert_sign
from .function.clone import clone_wellbore_axes
from .models import *
from .serializer import *
from django.http import JsonResponse
from rest_framework import generics, viewsets, mixins
from rest_framework.response import Response
from rest_framework.views import APIView

from Field.models import Run
from datetime import datetime

class DeviceListView(viewsets.ViewSet):
    """ Получить все телесистемы с коэффициентами """
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

    @swagger_auto_schema(tags=['Телесистема'], operation_summary="Получить все телесистемы", )
    def list(self, request):
        serializer = DeviceSerializer(self.queryset, many=True)
        return Response(serializer.data)


class DeviceCoefApiView(APIView):
    """ Коэффициенты телесистемы по id рейса """

    @swagger_auto_schema(tags=['Телесистема'],
                         operation_summary="Получить коэффициенты телесистемы по id рейса", )
    def get(self, request, run_id):
        try:
            d = AxesFileIndex.objects.get(run=run_id).device
            return JsonResponse({'device_title': d.device_title,
                                 'CX': d.CX,
                                 'CY': d.CY,
                                 'CZ': d.CZ,
                                 'BX': d.BX,
                                 'BY': d.BY,
                                 'BZ': d.BZ})
        except Exception as e:
            print(e)
            return JsonResponse({'status': 'Коэффициенты не найдены'})

    @swagger_auto_schema(tags=['Телесистема'],
                         operation_summary="Записать новые коэффициенты по id рейса",
                         request_body=openapi.Schema(
                             type=openapi.TYPE_OBJECT,
                             properties={
                                 'device_title': openapi.Schema(type=openapi.TYPE_STRING, description='Наименование'),
                                 'CX': openapi.Schema(type=openapi.TYPE_STRING, description='Коэф. GX'),
                                 'CY': openapi.Schema(type=openapi.TYPE_STRING, description='Коэф. GY'),
                                 'CZ': openapi.Schema(type=openapi.TYPE_STRING, description='Коэф. GZ'),
                                 'BX': openapi.Schema(type=openapi.TYPE_STRING, description='Коэф. BX'),
                                 'BY': openapi.Schema(type=openapi.TYPE_STRING, description='Коэф. BY'),
                                 'BZ': openapi.Schema(type=openapi.TYPE_STRING, description='Коэф. BZ'),
                             }
                         ),
                         Response={200: 'Коэффициенты записаны'}
                         )
    def post(self, request, run_id):
        # print(request.POST.dict())
        try:
            run = Run.objects.get(id=run_id)
        except:
            return JsonResponse({'status': f'Рейс с id {run_id} не найден'})
        t = AxesFileIndex.objects.get_or_create(run=run)
        if t[0].device is None:
            d = Device.objects.create(device_title=request.POST['device_title'],
                                      CX=request.POST['CX'],
                                      CY=request.POST['CY'],
                                      CZ=request.POST['CZ'],
                                      BX=request.POST['BX'],
                                      BY=request.POST['BY'],
                                      BZ=request.POST['BZ'])
            d.save()
            t[0].device = d
            t[0].save()
        else:
            t[0].device.device_title = request.POST.get('device_title')
            t[0].device.CX = request.POST.get('CX')
            t[0].device.CY = request.POST.get('CY')
            t[0].device.CZ = request.POST.get('CZ')
            t[0].device.BX = request.POST.get('BX')
            t[0].device.BY = request.POST.get('BY')
            t[0].device.BZ = request.POST.get('BZ')
            t[0].device.save()

        return request


@method_decorator(name='create',
                  decorator=swagger_auto_schema(tags=['Оси'], operation_summary="Добавить замер"))
@method_decorator(name='update',
                  decorator=swagger_auto_schema(tags=['Оси'], operation_summary="Обновить данные замера по id"))
@method_decorator(name='destroy',
                  decorator=swagger_auto_schema(tags=['Оси'], operation_summary="Удалить данные замера по id"))
@method_decorator(name='retrieve',
                  decorator=swagger_auto_schema(tags=['Оси'], operation_summary="Получить данные замера по id"))
class DataViewSet(viewsets.ModelViewSet):
    """Работа с осями"""
    queryset = Data.objects.all()
    serializer_class = DataSerializer


class DataByRunAPIView(APIView):
    """Получаем/заполняем замеры осей по id рейса"""

    @swagger_auto_schema(tags=['Оси'],
                         operation_summary="Получить все замеры по id рейса")
    def get(self, request, run_id):
        measurement = Data.objects.filter(run=run_id)
        return Response(DataSerializer(measurement, many=True).data)

    @swagger_auto_schema(tags=['Оси'],
                         operation_summary="Записать новые замеры по id рейса",)
    def post(self, request, run_id):
        try:
            current_run = Run.objects.get(id=run_id)
        except Run.DoesNotExist:
            return Response({'status': f'Рейс с id {run_id} не найден'})
        update_obj = list()
        print('rrrr', request.data)
        for meas in request.data:
            bd_data = Data.objects.get_or_create(depth=meas['depth'], run=current_run)
            update_obj.append(bd_data[0])
            bd_data[0].CX = meas['CX']
            bd_data[0].CY = meas['CY']
            bd_data[0].CZ = meas['CZ']
            bd_data[0].BX = meas['BX']
            bd_data[0].BY = meas['BY']
            bd_data[0].BZ = meas['BZ']
            bd_data[0].in_statistics = meas['in_statistics']
            bd_data[0].comment = meas['comment']
            bd_data[0].DIP_corr = meas['DIP_corr']
            bd_data[0].Btotal_corr = meas['Btotal_corr']
            Data.objects.bulk_update(update_obj, ["CX", "CY", "CZ", "BX", "BY", "BZ", "in_statistics",
                                                  "comment", "DIP_corr", "Btotal_corr"])
        return JsonResponse({'status': 'ok'})


class RawDataByRunAPIView(APIView):
    """Получаем сырые замеры осей по id рейса"""
    @swagger_auto_schema(tags=['Оси'],
                         operation_summary="Получить сырые замеры осей (до пересчета)")
    def get(self, request, run_id):
        raw_data = list()
        try:
            data = Data.objects.filter(run=run_id)
            index = AxesFileIndex.objects.get(run=run_id)
        except AxesFileIndex.DoesNotExist:
            return JsonResponse({'warning': 'Не найдены коэффициенты пересчёта для замеров данного рейса!'})
        coef = index.device

        for meas in data:
            raw_data.append({
                "id": meas.id,
                "depth": meas.depth,
                "CX_raw": eval(str(meas.CX) + convert_sign(coef.CX)),
                "CY_raw": eval(str(meas.CY) + convert_sign(coef.CY)),
                "CZ_raw": eval(str(meas.CZ) + convert_sign(coef.CZ)),
                "BX_raw": eval(str(meas.BX) + convert_sign(coef.BX)),
                "BY_raw": eval(str(meas.BY) + convert_sign(coef.BY)),
                "BZ_raw": eval(str(meas.BZ) + convert_sign(coef.BZ)),
                "run_id": run_id,
                "telesystem_id": index.device.id,
            })

        return Response(raw_data)


# axes/api/wellbore_copy
def wellbore_copy(request):
    """ По fetch запросу с клиента клонируются замеры ствола c осями
    (в request должны лежать id нового и старого стволов, сама модель Wellbore создается в модуле Field заранее)"""
    clone_wellbore_axes(request)
    return JsonResponse({'status': 'ok'})


# axes/api/addAxes
def add_Axes(request):
    """По fetch запросу добавляем новые оси"""
    if request.method == 'POST':  # Модальная форма с ОСЯМИ
        current_run = Run.objects.get(id=request.POST['run'])
        axes_data = request.POST['data-axes'].replace(',', '.'). \
            replace(' ', '').replace('\r', '').replace('\n', '\t').replace('\t\t', '\t').split('\t')
        # print(axes_data)
        counter = 0
        manually_bz = list()
        manually_by = list()
        manually_bx = list()
        manually_gz = list()
        manually_gy = list()
        manually_gx = list()
        manually_depth = list()
        for data in axes_data:
            if data == '':
                continue
            if counter == 0:
                manually_depth.append(data)
            elif counter == 1:
                manually_gx.append(data)
            elif counter == 2:
                manually_gy.append(data)
            elif counter == 3:
                manually_gz.append(data)
            elif counter == 4:
                manually_bx.append(data)
            elif counter == 5:
                manually_by.append(data)
            else:
                manually_bz.append(data)
            counter = (0 if counter == 6 else counter + 1)
        # result - считанные данные
        result = list(zip(manually_depth, manually_gx, manually_gy, manually_gz, manually_bx, manually_by, manually_bz))
        result2 = new_measurements(result, request.POST.get('device'))  # перобразованные данные

        if request.POST.get('device') != '-----' and request.POST.get('device') != '':
            telesystem_ind = AxesFileIndex.objects.get(run_id=current_run)
            telesystem_ind.device = Device.objects.get(device_title=request.POST.get('device'))
            telesystem_ind.save()
            result2 = new_measurements(result, request.POST.get('device'))  # перобразованные данные
            conflict, date = write_to_bd(result2, current_run)
        else:
            conflict, date = write_to_bd(result, current_run)

        if len(conflict['old']) > 0:
            print('Открыть модальное окно!')
            return JsonResponse({'warning': 'Изменились значения осей!', 'conflict': conflict, 'date': str(date)})
        else:
            return JsonResponse({'status': 'ok'})
    return JsonResponse({'warning': 'Обратитесь к POST методу!'})


def update_Axes(request):
    """По fetch запросу обновляем оси"""
    # print(request.POST.dict())
    try:
        obj = Data.objects.get(run=request.POST['run_id'], depth=request.POST['depth'])

        Conflict.objects.create(
            depth=obj.depth,
            run_id=obj.run.id,
            CX=obj.CX,
            CY=obj.CY,
            CZ=obj.CZ,
            BX=obj.BX,
            BY=obj.BY,
            BZ=obj.BZ,
            date=obj.date,
            Btotal_corr=obj.Btotal_corr,
            DIP_corr=obj.DIP_corr,
            in_statistics=obj.in_statistics,
            comment=obj.comment
        )
        if request.POST['date'] == "0":
            obj.date = datetime.now()
        else:
            obj.date = request.POST['date']
        obj.CX = request.POST['CX']
        obj.CY = request.POST['CY']
        obj.CZ = request.POST['CZ']
        obj.BX = request.POST['BX']
        obj.BY = request.POST['BY']
        obj.BZ = request.POST['BZ']
        obj.save()
    except Data.DoesNotExist:
        return JsonResponse({"warning": "Ошибка перезаписи."})

    return JsonResponse({"status": f"Замер с ID:{obj.id} успешно перезаписан!"})

def reset_data(request):

    try:
        data = Data.objects.filter(run=request.POST['run_id'], date=request.POST['date'])
        for element in data:
            try:
                conflictElement = Conflict.objects.filter(run=request.POST['run_id'], depth=element.depth).last()
                Data.objects.get(id=element.id).delete()
                if conflictElement:
                    Data.objects.create(
                        depth=conflictElement.depth,
                        run= conflictElement.run,
                        CX= conflictElement.CX,
                        CY=conflictElement.CY,
                        CZ=conflictElement.CZ,
                        BX=conflictElement.BX,
                        BY=conflictElement.BY,
                        BZ=conflictElement.BZ,
                        date=conflictElement.date,
                        in_statistics = conflictElement.in_statistics
                    )
                    Conflict.objects.get(id=conflictElement.id).delete()
            except Conflict.DoesNotExist:
                Data.objects.get(id=element.id).delete()

        return JsonResponse({'status': 'ok'})
    except Data.DoesNotExist:
        return JsonResponse({"warning": "Ошибка отката."})