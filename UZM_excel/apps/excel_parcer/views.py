from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage

from .forms import AddDeviceForm
from .function.functions import *

from django.http import JsonResponse, HttpResponse
import re
from Field.views_api import get_tree
from Field.models import Well, Run, Wellbore, Run, get_all_run, Section, get_all_well
from .models import Data, AxesFileIndex, Device
from datetime import timedelta, datetime, timezone


def index(request):
    """
    Оси вывод по рейсам данных
    """
    context = {"title": 'Оси',
               "tree": get_tree(),
               'selected_run': 'None',
               'error_depth': list(),  # глубины замеров при вставке которых нашли ошибку
               "telesystem": Device.objects.all(),
               }
    # устанавливаем начальное значение макс даты
    date_max = 0
    if request.method == 'POST':
        # получение данных для отображения
        try:
            current_run = Run.objects.get(id=request.POST['run'])
            context['title'] = current_run.section.wellbore.well_name.get_title()
        except Exception as e:
            print(e)
            return render(request, 'excel_parcer/axes.html', {'context': context, 'date_max': date_max,})
        context['well'] = current_run.section.wellbore.well_name
        context['selected_run'] = current_run
        context['data'] = Data.objects.filter(run=request.POST['run'], in_statistics=1).order_by('depth')
        lastElem = Data.objects.filter(run=request.POST['run'], in_statistics=1).order_by('depth').last()
        # находим записи, котрые были добавлены в поледний час, это нужно для кнопки Откатить
        if lastElem and lastElem.date is not None:
            date_max_last = lastElem.date
            dif_date = datetime.now(timezone.utc) - date_max_last
            if dif_date.total_seconds() <= 3600 and (date_max == 0 or date_max < date_max_last):
                date_max = date_max_last



        if 'depth' in request.POST:  # Модальная форма с скорректированными значениями
            depth_data = request.POST['depth'].replace(',', '.').replace(' ', '').replace('\r', ''). \
                replace('\n', '\t').split('\t')
            Btotal_data = request.POST['Btotal_corr'].replace(',', '.').replace(' ', '').replace('\r', ''). \
                replace('\n', '\t').split('\t')
            DIP_data = request.POST['DIP_corr'].replace(',', '.').replace(' ', '').replace('\r', ''). \
                replace('\n', '\t').split('\t')
            for meas in zip(depth_data, Btotal_data, DIP_data):
                if meas[0] != '' and meas[1] != '' and meas[2] != '':
                    try:
                        obj = Data.objects.get(run=current_run, depth=float(meas[0]))
                        obj.Btotal_corr = (float(meas[1]) if float(meas[1]) > 100 else float(meas[1]) * 1000)
                        obj.DIP_corr = float(meas[2])
                        obj.save()
                    except:
                        context['error_depth'].append(float(meas[0]))
    return render(request, 'excel_parcer/axes.html', {'context': context, 'date_max': date_max,})


def edit_index(request):
    """Редактировать таблицу с осями и скорректирвоанными значениями"""
    context = {"title": 'Оси',
               'selected_run': 'None',
               }

    if request.method == 'GET':
        if request.GET.get('run_id'):
            current_run = Run.objects.get(id=request.GET.get('run_id'))
            context['well'] = current_run.section.wellbore.well_name
            context['data'] = Data.objects.filter(run=current_run, in_statistics=1).order_by('depth')
            context['selected_run'] = current_run

    # FIXME
    if request.method == 'POST':
        for items in request.POST.lists():
            key = str(items[0]).split(' ')
            try:
                obj = Data.objects.get(id=key[0])
            except:
                print('Замер уже удалён')
                continue

            if items[1][0] == '':
                if key[1] == 'btotal':
                    obj.Btotal_corr = None
                    obj.save()
                elif key[1] == 'dip':
                    obj.DIP_corr = None
                    obj.save()
                else:
                    obj.delete()
            else:
                if key[1] == 'depth':
                    obj.depth = items[1][0]
                elif key[1] == 'gx':
                    obj.CX = items[1][0]
                elif key[1] == 'gy':
                    obj.CY = items[1][0]
                elif key[1] == 'gz':
                    obj.CZ = items[1][0]
                elif key[1] == 'bx':
                    obj.BX = items[1][0]
                elif key[1] == 'by':
                    obj.BY = items[1][0]
                elif key[1] == 'bz':
                    obj.BZ = items[1][0]
                elif key[1] == 'btotal':
                    obj.Btotal_corr = items[1][0]
                elif key[1] == 'dip':
                    obj.DIP_corr = items[1][0]
                obj.save()
        return redirect('axes')
    return render(request, 'excel_parcer/edit_axes.html', {'context': context, })


def settings(request):
    """Настройки импорта файлов с осями"""
    context = {"telesystem": Device.objects.all(),
               "tree": get_tree(),
               "title": 'Загрузка осей',
               }

    if request.method == 'POST':
        update_values = {'GX': request.POST.get('inp_gx'),
                         'GY': request.POST.get('inp_gy'),
                         'GZ': request.POST.get('inp_gz'),
                         'BX': request.POST.get('inp_bx'),
                         'BY': request.POST.get('inp_by'),
                         'BZ': request.POST.get('inp_bz'),
                         'depth': request.POST.get('inp_depth'),
                         'units': request.POST.get('inp_measurement'),
                         'string_index': request.POST.get('inp_import'),
                         'device': Device.objects.get(device_title=request.POST.get('device'))}
        AxesFileIndex.objects.update_or_create(run=request.POST.get('run_id'), defaults=update_values)
    return render(request, 'excel_parcer/settings.html', {'context': context, })


def add_Device(request):
    """Добавление телесистемы"""
    context = {"telesystem": Device.objects.all(),
               "title": 'Телесистема',
               "form": AddDeviceForm(request.POST),
               }

    if request.method == 'POST':
        if context['form'].is_valid():
            context['form'].save()
    return render(request, 'excel_parcer/device.html', {'context': context, })


def graph(request):
    """Страница с графиком первичного контроля"""
    context = {'title': 'Контроль качества', "tree": get_tree(), 'depthGoxy': list(),
               'depthGz': list(), 'depthGtotal': list(), 'depthGref': list(), 'depthGmax': list(), 'depthGmin': list(),
               'depthBoxy': list(), 'depthBz': list(), 'depthBtotal': list(), 'depthBref': list(), 'depthBmax': list(),
               'depthBmin': list(), 'depthBcorr': list(), 'depthDipraw': list(), 'depthDipref': list(),
               'depthDipmax': list(), 'depthDipmin': list(), 'depthDipcorr': list(), 'depthHSTF': list(),
               'selected': 'None'}

    if request.method == 'POST' and request.POST['wellbore'] != '':
        wellbore = Wellbore.objects.get(id=request.POST['wellbore'])
        context['title'] = wellbore.well_name.get_title()
        runs = Run.objects.filter(section__wellbore=wellbore)
        context['selected'] = wellbore
        for run in runs:
            surveys = Data.objects.filter(run=run)
            for survey in surveys:
                # График Goxy-Gz
                context['depthGoxy'].append({'x': survey.depth, 'y': survey.get_goxy()})
                context['depthGz'].append({'x': survey.depth, 'y': survey.CZ})
                # График Gtotal
                context['depthGtotal'].append({'x': survey.depth, 'y': survey.Gtotal()})
                context['depthGref'].append({'x': survey.depth, 'y': wellbore.well_name.gtotal_graph()})
                context['depthGmax'].append({'x': survey.depth, 'y': wellbore.well_name.max_gtotal()})
                context['depthGmin'].append({'x': survey.depth, 'y': wellbore.well_name.min_gtotal()})
                # График Boxy-Bz
                context['depthBoxy'].append({'x': survey.depth, 'y': survey.get_boxy()})
                context['depthBz'].append({'x': survey.depth, 'y': survey.BZ})
                # График Btotal
                context['depthBtotal'].append({'x': survey.depth, 'y': survey.Btotal()})
                context['depthBref'].append({'x': survey.depth, 'y': wellbore.well_name.btotal_graph()})
                context['depthBmax'].append({'x': survey.depth, 'y': wellbore.well_name.max_btotal()})
                context['depthBmin'].append({'x': survey.depth, 'y': wellbore.well_name.min_btotal()})
                context['depthBcorr'].append({'x': survey.depth, 'y': (survey.Btotal_corr if
                                                                       survey.Btotal_corr is not None else 'Null')})
                # График HSTF
                context['depthHSTF'].append({'x': survey.depth, 'y': survey.get_hstf()})
                # График Dip
                context['depthDipraw'].append({'x': survey.depth, 'y': survey.Dip()})
                context['depthDipref'].append({'x': survey.depth, 'y': wellbore.well_name.dip_graph()})
                context['depthDipmax'].append({'x': survey.depth, 'y': wellbore.well_name.max_dip()})
                context['depthDipmin'].append({'x': survey.depth, 'y': wellbore.well_name.min_dip()})
                context['depthDipcorr'].append({'x': survey.depth, 'y': (survey.DIP_corr if
                                                                         survey.DIP_corr is not None else 'Null')})

    try:
        context['firstDepth'] = context['depthHSTF'][0]['x']
        context['lastDepth'] = context['depthHSTF'][-1]['x']
    except IndexError:
        context['firstDepth'] = context['lastDepth'] = 0

    return render(request, 'excel_parcer/graph.html', {'context': context, })


def uploadAxesFile(request):
    """ Функция для чтения замеров с осями из переданного файла"""
    if request.method == 'POST':
        if 'file' in request.FILES:
            doc = request.FILES['file']
            fs = FileSystemStorage()
            file_name = fs.save(doc.name, doc)
            current_run = Run.objects.get(id=request.POST.get('run_id'))
            try:
                telesystem = AxesFileIndex.objects.get(run=current_run)
                NoneCorrectItems = {None, ''}
                Items = {telesystem.depth, telesystem.GX, telesystem.GY, telesystem.GZ, telesystem.BX,
                         telesystem.BY, telesystem.BZ, telesystem.string_index, telesystem.device}
                if len(NoneCorrectItems.intersection(Items)) != 0:
                    raise AxesFileIndex.DoesNotExist
            except AxesFileIndex.DoesNotExist:
                return JsonResponse({'warning': 'Ошибка чтения! Пожалуйста, проверьте настройки импорта для '
                                                'выбранного рейса!'})
            # данные которые пришли
            result = parcing_manually("./media/" + file_name,
                                      telesystem.depth,
                                      telesystem.GX,
                                      telesystem.GY,
                                      telesystem.GZ,
                                      telesystem.BX,
                                      telesystem.BY,
                                      telesystem.BZ,
                                      telesystem.string_index,
                                      )
            # обнавлённые данные с учётом старых
            result2 = new_measurements(result, telesystem.device.device_title)
            conflict, date = write_to_bd(result2, current_run)
            if len(conflict['old']) > 0:
                # print(f'Замена замеров, status: Открыть модальное окно!')
                return JsonResponse({'conflict_warning': 'Изменились значения осей!', 'conflict': conflict, 'date':str(date)})
    return JsonResponse({'status': 'ok'})


def axes_comm(request):
    """Функция для добавления комментария к замерам осей"""
    obj = Data.objects.get(id=request.POST['id'])
    obj.comment = request.POST['comment']
    obj.save()
    return JsonResponse({'status': 'ok'})


def del_Meas(request):
    """Удаление замеров POST методом"""
    for key, value in request.POST.dict().items():
        Data.objects.get(id=key).delete()
    return JsonResponse({'status': 'ok'})


def del_Device(request):
    """Удаление телистемы по id"""
    dev = Device.objects.get(id=request.POST['device_id']).delete()
    return JsonResponse({'status': 'ok'})


def get_coef_device(request):
    """api для fetch запроса
    Получаем коэффициенты
    """
    try:
        device = Device.objects.get(device_title=request.POST.get('device_title'))
    except:
        return JsonResponse({'status': str(request.POST.get('device_title')) + '- такой телесистемы нет', })

    return JsonResponse({
        'GX': device.CX,
        'GY': device.CY,
        'GZ': device.CZ,
        'BX': device.BX,
        'BY': device.BY,
        'BZ': device.BZ,
    })


def get_run_index(request):
    """Api для fetch запроса
    Получаем индексы для выбранного рейса
    """
    # print(request.POST.get('run_id'))
    if request.method == 'POST':
        telesystem_tuple = AxesFileIndex.objects.get_or_create(run=Run.objects.get(id=request.POST.get('run_id')))
        telesystem_index = telesystem_tuple[0]
        try:
            return JsonResponse({
                'GX': telesystem_index.GX,
                'GY': telesystem_index.GY,
                'GZ': telesystem_index.GZ,
                'BX': telesystem_index.BX,
                'BY': telesystem_index.BY,
                'BZ': telesystem_index.BZ,
                'unit': telesystem_index.units,
                'string': telesystem_index.string_index,
                'depth': telesystem_index.depth,
                'device': telesystem_index.device.device_title, })
        except Exception as e:
            return JsonResponse({
                'GX': [],
                'GY': [],
                'GZ': [],
                'BX': [],
                'BY': [],
                'BZ': [],
                'unit': [],
                'string': [],
                'depth': [],
                'device': [],
            })
