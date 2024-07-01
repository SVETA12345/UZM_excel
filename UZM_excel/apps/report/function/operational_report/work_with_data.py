import os
import re
from typing import NoReturn
import numpy as np

from django.core.files.storage import FileSystemStorage
from django.http import FileResponse, HttpResponse

from report.function.operational_report.work_with_Excel import excel_open, write_data_in_Excel
from report.models import ReportIndex, DynamicNNBData, Raw, IgirgiStatic, StaticNNBData, Plan, get_run_by_id, IgirgiDynamic, \
    InterpPlan
from report.function.model_service import get_data
from Field.models import Run
import lasio

file_dir = os.getcwd() + "\\files"

# словарь универсальных значений под импортируемые файлы ключ(то чем мы пользуемся)-значение(имя с формы)
file_dict = {'igirgi': 'igirgi_file',
             'nnb': 'nnb_file',
             'raw': 'raw_file',
             'plan': 'plan_file'
             }

data_name = {'igirgi_file': 'Статические замеры ИГИРГИ',
             'nnb_dynamic': 'Динамические замеры ННБ',
             'nnb_static': 'Статические замеры ННБ',
             'raw_file': 'Сырые динамические замеры',
             'plan_file': 'Плановая траектория',
             'igirgi_dynamic': 'Динамические замеры ИГИРГИ',
             }


def rewrite_ReportIndex(new_index: dict()) -> id:
    """Перезапись индексов в базе"""

    obj = Run.objects.get(id=new_index['run'])
    index_model = ReportIndex.objects.get_or_create(run=obj)[0]

    if new_index["raw_str"] != '':
        index_model.raw_str = int(new_index["raw_str"])
        index_model.raw_dynamic_list_name = new_index["raw_list_name"]
        index_model.raw_dynamic_depth_excel = new_index["raw_depth_excel"]
        index_model.raw_dynamic_corner_excel = new_index["raw_corner_excel"]
    else:
        index_model.raw_dynamic_depth = new_index["raw_depth"]
        index_model.raw_dynamic_corner = new_index["raw_corner"]
        index_model.raw_list_name = new_index["raw_list_name"]

    index_model.nnb_static_read = int(new_index["nnb_static_read"])
    index_model.nnb_static_depth = new_index["nnb_static_depth"]
    index_model.nnb_static_corner = new_index["nnb_static_corner"]
    index_model.nnb_static_azimut = new_index["nnb_static_azimut"]
    index_model.nnb_static_list_name = new_index["nnb_static_list_name"]

    if new_index["nnb_dynamic_read"] != '':
        index_model.nnb_dynamic_read = int(new_index["nnb_dynamic_read"])
    index_model.nnb_dynamic_depth = new_index["nnb_dynamic_depth"]
    index_model.nnb_dynamic_corner = new_index["nnb_dynamic_corner"]
    index_model.nnb_dynamic_azimut = new_index["nnb_dynamic_azimut"]
    index_model.nnb_dynamic_list_name = new_index["nnb_dynamic_list_name"]

    index_model.igirgi_static_depth = new_index["igirgi_static_depth"]
    index_model.igirgi_static_corner = new_index["igirgi_static_corner"]
    index_model.igirgi_static_azimut = new_index["igirgi_static_azimut"]
    index_model.igirgi_list_name = new_index["igirgi_static_list_name"]

    if new_index["igirgi_str"] != '':
        index_model.igirgi_str = int(new_index["igirgi_str"])

    index_model.plan_depth = new_index["plan_depth"]
    index_model.plan_corner = new_index["plan_corner"]
    index_model.plan_azimut = new_index["plan_azimut"]
    index_model.plan_list_name = new_index["plan_list_name"]
    index_model.plan_str = new_index["plan_str"]
    index_model.save()
    return index_model.id


def clear_folder(path: str) -> NoReturn:
    """Удаляем все файлы в указанной папке"""
    for f in os.listdir(path):
        os.remove(os.path.join(path, f))


def work_with_file(request, run_id: int, index_id: int, igirgi_data: list = None) -> HttpResponse | FileResponse:
    """ Общая цель: обработка импортируемых файлов и выдача отчета
        Примечания: это необходимая функция для выдачи файла.
        Здесь с БД под каждый файл подтягиваются индексы для считывания данных.
    """

    # сохранение подаваемых файлов и заполнения данных о их расположении в processing_param
    if 'nnb_file' not in request.FILES and \
            'plan_file' not in request.FILES and \
            ('igirgi_file' not in request.FILES or igirgi_data is None):
        return HttpResponse('Нехватка важного файла!')

    # clear_folder(file_dir + '/Report_input')  # чистим старые файлы
    fs = FileSystemStorage(location=file_dir + '/Report_input')
    processing_param = dict()
    if igirgi_data is None:  # если нет вручную написанных данных ищем в файле
        igirgi_file = request.FILES[file_dict['igirgi']]
        processing_param['igirgi_file'] = fs.save('igirgi_' + igirgi_file.name, igirgi_file)
    else:
        processing_param['igirgi_data'] = igirgi_data

    nnb_file = request.FILES[file_dict['nnb']]  # сохранение nnb замеров
    processing_param[file_dict['nnb']] = fs.save('nnb_' + nnb_file.name, nnb_file)

    plan_file = request.FILES[file_dict['plan']]  # сохранение плана
    processing_param[file_dict['plan']] = fs.save('plan_' + plan_file.name, plan_file)

    if file_dict['raw'] in request.FILES:  # проверка сырых динамических замеров
        raw_file = request.FILES[file_dict['raw']]
        processing_param[file_dict['raw']] = fs.save('raw_' + raw_file.name, raw_file)
        processing_param["response_type"] = "full_version"
    else:
        processing_param["response_type"] = "cut_version"

    return processing_data(processing_param, run_id, index_id)


def processing_data(start_data: dict, run_id: int, index_id: int) -> FileResponse:
    """Общая цель: обработка входных данных/генерация отчета
       На входе: dict()
            key: тип файла (один из file_dict)
            value: путь до файла

       На выходе: FileResponse (тот самый, что вы видим на странице)
    """
    all_data = dict()  # цель - получить словарь данных в нужном формате
    # ('Тип файла': ('Колонка':[Данные]))

    # обработка полученных файлов, запись всех данных в all_data
    for key, value in start_data.items():
        print(f'Работа с type: {key} - file: {value}')
        if key == 'response_type':
            pass  # для выдачи нужного шаблона
        elif key == "igirgi_data":
            all_data['Статические замеры ИГИРГИ'] = list_to_dict(value)
        else:
            data = reader(key, value, index_id)
            if 'Динамические' in data and 'Статические' in data:
                if start_data["response_type"] != "cut_version":
                    all_data[data_name['nnb_dynamic']] = data['Динамические']
                all_data[data_name['nnb_static']] = data['Статические']
            else:
                all_data[data_name[key]] = data

    # создание и обработка данных
    if start_data["response_type"] != "cut_version":
        all_data['Сырые динамические замеры'] = raw_filter(all_data['Сырые динамические замеры'])
        all_data['Динамические замеры ИГИРГИ'] = do_dynamic_igirgi(all_data['Статические замеры ИГИРГИ'],
                                                                   all_data['Сырые динамические замеры'])

    # добавим к данным ИГиРГИ 0 в начало, если его нет
    if all_data['Статические замеры ИГИРГИ']['Глубина'][0] != 0:
        all_data['Статические замеры ИГИРГИ']['Глубина'] = [0, *all_data['Статические замеры ИГИРГИ']['Глубина']]
        all_data['Статические замеры ИГИРГИ']['Угол'] = [0, *all_data['Статические замеры ИГИРГИ']['Угол']]
        all_data['Статические замеры ИГИРГИ']['Азимут'] = [0, *all_data['Статические замеры ИГИРГИ']['Азимут']]

    if all_data['Статические замеры ННБ']['Глубина'][-1] not in all_data['Статические замеры ИГИРГИ']['Глубина']:
        all_data['Статические замеры ННБ']['Глубина'].pop(-1)
        all_data['Статические замеры ННБ']['Угол'].pop(-1)
        all_data['Статические замеры ННБ']['Азимут'].pop(-1)

    # запись в бд
    bd_Write_data(all_data, run_id)
    run_obj = Run.objects.get(id=run_id)

    # перезапись данных (расширение подаваемых значений, данными БД)
    all_data = get_data(run_obj)
    # выдача файлов на скачивание
    file_type = 0 if start_data["response_type"] == "cut_version" else 1
    file_name, waste = write_data_in_Excel(all_data, f'Единая_форма_отчета.xlsx', run_obj)
    return FileResponse(open(file_dir + "\\Report_out\\" + file_name, 'rb'))


def reader(key: str, value: str, run_index_id: int) -> dict:
    """Общая цель: подбор параметров под чтение файлов из ReportIndex,
       чтение и возврат словаря.
       На входе: dict()
                key: тип файла - на его основе подбор параметров
                value: путь к файлу

       На выходе:dict()
                key: Имя столбца
                value: Лист с данными

    """
    colum_name = ReportIndex.objects.get(id=run_index_id)

    if 'igirgi_file' == key:
        var = {'Глубина': colum_name.igirgi_static_depth,
               'Угол': colum_name.igirgi_static_corner,
               'Азимут': colum_name.igirgi_static_azimut,
               'Строка': colum_name.igirgi_str,
               'Лист': colum_name.igirgi_list_name,
               'Имя файла': value, }
    elif 'nnb_file' == key:
        dynamic = []
        var = {'Глубина': colum_name.nnb_static_depth,
               'Угол': colum_name.nnb_static_corner,
               'Азимут': colum_name.nnb_static_azimut,
               'Строка': colum_name.nnb_static_read,
               'Лист': colum_name.nnb_static_list_name,
               'Имя файла': value, }
        static = excel_open(var)
        # если мы не задавали параметры для считывания динамических замеров значит их нет
        if colum_name.nnb_dynamic_list_name != '' and colum_name.nnb_dynamic_read is not None:
            var = {'Глубина': colum_name.nnb_dynamic_depth,
                   'Угол': colum_name.nnb_dynamic_corner,
                   'Азимут': colum_name.nnb_dynamic_azimut,
                   'Строка': colum_name.nnb_dynamic_read,
                   'Лист': colum_name.nnb_dynamic_list_name,
                   'Имя файла': value, }
            dynamic = excel_open(var)
        return {'Статические': static, 'Динамические': dynamic}
    elif 'raw_file' == key:
        var = {'Глубина': colum_name.raw_dynamic_depth,
               'Угол': colum_name.raw_dynamic_corner,
               'Строка': colum_name.raw_str,
               'Лист': colum_name.raw_dynamic_list_name,
               'Имя файла': value,
               }
    elif 'plan_file' == key:
        var = {'Глубина': colum_name.plan_depth,
               'Угол': colum_name.plan_corner,
               'Азимут': colum_name.plan_azimut,
               'Строка': colum_name.plan_str,
               'Лист': colum_name.plan_list_name,
               'Имя файла': value,
               }
    else:
        print("\033[33m\033[1m {}".format(f'Неизвестный тип файла с типом:{key}  имя файла:{value}'))

    # непосредственно обработчик файлов
    if "las" in re.findall(r".(las)", value):
        return las_reader(var)
    else:
        return excel_open(var)


def las_reader(column: dict()) -> dict:
    """Чтение las файлов на основе переданных параметров

    На входе:
        'Глубина'  - имя столбца с глубиной
        'Угол'     - имя столбца с угом
        'Азимут'   - имя столбца с азимутом (опционально)
        'Имя файла'- имя файла для считывания из папки UZM_excel\Files\Report_input

    На выходе: (если найдем имя столбца в файле)
        'Глубина'  - Данные [1,2,3..,4]
        'Угол'     - Данные [1,2,3..,4]
        'Азимут'   - Данные [1,2,3..,4]
    """
    result = {}

    filename = column['Имя файла']
    file_folder = file_dir + '\\Report_input\\' + filename
    las_file = lasio.read(file_folder)

    for key, value in column.items():
        if value in las_file.keys():
            result[key] = np.array(las_file[value])
    return result


# def find_place(wbSheet, r: int) -> int:
#     """ Рекурсивная функция поиска свободной колонки на странице эксель файла
#      для заполнения данными"""
#     global c
#     if wbSheet.cell(row=r, column=c).value is None:
#         return r
#     else:
#         c += 1
#         find_place(wbSheet, r)


def raw_filter(data: dict) -> dict:
    """Фильтруем массив от выбросов и нулевых значений"""
    nan_mask = np.isnan(data['Угол'])
    # print(nan_mask)
    not_nan_mask = ~nan_mask
    data['Угол'] = data['Угол'][not_nan_mask]
    data['Глубина'] = data['Глубина'][not_nan_mask]

    return data


def list_to_dict(data_list: list) -> dict:
    """Функция для обработки и преобразования данных Статических замеров ИГиРГИ
       введенных вручную
    """
    result = {'Глубина': [],
              'Угол': [],
              'Азимут': []}
    count = 1
    for element in data_list:
        if count == 1:
            try:
                result['Глубина'].append(float(element))
            except Exception as e:
                print(f'Ошибка в функции преобразованнии ручного ввода: '
                      f'Элемент ошибки:{element}/ Ошибка: {e}')
        if count == 2:
            try:
                result['Угол'].append(float(element))
            except Exception as e:
                print(f'Ошибка в функции преобразованнии ручного ввода: '
                      f'Элемент ошибки:{element}/ Ошибка: {e}')
        if count == 3:
            try:
                result['Азимут'].append(float(element))
            except Exception as e:
                print(f'Ошибка в функции преобразованнии ручного ввода: '
                      f'Элемент ошибки:{element}/ Ошибка: {e}')
            count = 0
        count += 1

    result['Глубина'] = np.array(result['Глубина'])
    result['Угол'] = np.array(result['Угол'])
    result['Азимут'] = np.array(result['Азимут'])
    return result


def do_dynamic_igirgi(static: dict, row: dict) -> dict:
    """
    Из статических и сырых данных делаем динамические
    """
    return dynamic_from_interpolis(static, row)


def dynamic_from_interpolis(static: dict, row: dict):
    """Интерполяция значений"""
    data = {'Глубина': np.concatenate([row['Глубина'], static['Глубина']]),
            'Угол': np.concatenate([row['Угол'], static['Угол']])}

    x = np.concatenate([getx_From_static(static['Глубина']), static['Глубина']])
    x = np.sort(x)
    y = np.interp(x, data['Глубина'], data['Угол'])

    if 'Азимут' in row.keys():
        data['Азимут'] = np.concatenate([row['Азимут'], static['Азимут']])
        z = np.interp(x, data['Глубина'], data['Азимут'])
    else:
        z = np.interp(x, static['Глубина'], static['Азимут'])

    data['Глубина'] = list(x)
    data['Угол'] = list(y)
    data['Азимут'] = list(z)
    return data


def getx_From_static(data: list, part: int = 5) -> np.array:
    """
    Для функции интерполяции ищем значения глубины из которых нужно найти угол
    """
    count = 1
    result = []
    for i in data:
        if count < len(data):
            dx = (data[count] - i) / part
            count += 1
            for j in range(1, part):
                result.append(i + j * dx)
    return np.array(result)


def bd_Write_data(all_data: dict, run_id: int) -> NoReturn:
    """
    Записываем считанные данные в бд
    """
    # в run_id находится id модели с индексами,
    # через нее достанет объект рейса
    updat_obj = []

    for key in data_name.keys():
        if key == 'igirgi_file':
            model = IgirgiStatic
        elif key == 'nnb_dynamic':
            model = DynamicNNBData
        elif key == 'nnb_static':
            model = StaticNNBData
        elif key == 'raw_file':
            model = Raw
        elif key == 'plan_file':
            model = Plan
        elif key == 'igirgi_dynamic':
            model = IgirgiDynamic
        else:
            break

        if data_name[key] in all_data:
            data_dict = all_data[data_name[key]]
        else:
            continue

        Run = get_run_by_id(run_id)

        if 'Азимут' in data_dict.keys():
            for meas in list(zip(data_dict['Глубина'], data_dict['Угол'], data_dict['Азимут'])):
                # print(meas)
                db_meas = model.objects.get_or_create(depth=meas[0], run=Run)
                updat_obj.append(db_meas[0])
                db_meas[0].corner = meas[1]
                db_meas[0].azimut = meas[2]
            model.objects.bulk_update(updat_obj, ['corner', 'azimut'])
        else:
            for meas in list(zip(data_dict['Глубина'], data_dict['Угол'])):
                # print(meas)
                db_meas = model.objects.get_or_create(depth=meas[0], run=Run)
                updat_obj.append(db_meas[0])
                db_meas[0].corner = meas[1]
            model.objects.bulk_update(updat_obj, ['corner'])
        updat_obj = []


# Работа с файлом плановой траектории!

def bd_Write_plan(data_dict: dict, run_id: int, plan_version: str = None) -> NoReturn:
    """Записываем считанные данные плана в бд с припиской версии
    """
    updat_obj = []
    model = Plan
    Run = get_run_by_id(run_id)

    for meas in list(zip(data_dict['Глубина'], data_dict['Угол'], data_dict['Азимут'])):
        # print(meas)
        db_meas = model.objects.get_or_create(depth=meas[0], run=Run)
        updat_obj.append(db_meas[0])
        db_meas[0].corner = meas[1]
        db_meas[0].azimut = meas[2]
        db_meas[0].plan_version = plan_version
    model.objects.bulk_update(updat_obj, ['corner', 'azimut', 'plan_version'])


def work_with_plan(request: dict, run: object) -> bool:
    """Чтение и сохранение палновой траектории"""
    fs = FileSystemStorage(location=file_dir + '/Report_input')
    plan_file = request.FILES['plan_file']  # сохранение файла плана
    path = fs.save('plan_' + plan_file.name, plan_file)
    plan_index(run, request.POST)  # перезапись индексов
    # print('Начали читать план')
    data = reader('plan_file', path, ReportIndex.objects.get(run=run).id)  # берём данные с плана
    # удаляем старый план
    # print(data)
    plan_delete(run)
    bd_Write_plan(data, run.id, request.POST['plan_version'])  # сохраняем в бд
    # print('сохранили в бд')
    return True


def plan_delete(run):
    """
    Удаляем все замеры со ствола, к которому привязан переданный рейс.
    [Используется при загрузке нового плана/удалении старого]
    """
    runs = Run.objects.filter(section__wellbore=run.section.wellbore)
    Plan.objects.filter(run__in=runs).delete()
    InterpPlan.objects.filter(run__in=runs).delete()


def plan_index(run, new_index):
    """ Перезапись индексов палновой траектории """
    index_model = ReportIndex.objects.get_or_create(run=run)[0]
    index_model.plan_depth = new_index["plan_depth"]
    index_model.plan_corner = new_index["plan_corner"]
    index_model.plan_azimut = new_index["plan_azimut"]
    index_model.plan_list_name = new_index["plan_list_name"]
    index_model.plan_str = new_index["plan_str"]
    index_model.save()


# Работа с фалом траектории ННБ

def work_with_nnb(request: dict, run: object) -> bool:
    """ Читаем значения из файла внутри request """
    fs = FileSystemStorage(location=file_dir + '/Report_input')
    nnb_file = request.FILES['file']
    path = fs.save('nnb_' + nnb_file.name, nnb_file)
    data = reader('nnb_file', path, ReportIndex.objects.get(run=run).id)
    bd_Write_static_nnb(data['Статические'], run, ReportIndex.objects.get(run=run).nnb_static_exclude_proj)
    return True


def bd_Write_static_nnb(data_dict: dict, run: object, exclude_proj: bool = False) -> NoReturn:
    """Записываем считанные данные траектории ннб в бд
    """
    updat_obj = []
    model = StaticNNBData

    for meas in list(zip(data_dict['Глубина'], data_dict['Угол'], data_dict['Азимут'])):
        # print(meas)
        if exclude_proj and meas[0] == data_dict['Глубина'][-1]:  # не записываем последнмй замер
            continue
        db_meas = model.objects.get_or_create(depth=meas[0], run=run)
        updat_obj.append(db_meas[0])
        db_meas[0].corner = meas[1]
        db_meas[0].azimut = meas[2]

    model.objects.bulk_update(updat_obj, ['corner', 'azimut'])

