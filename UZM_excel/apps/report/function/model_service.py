import numpy as np
from math import sqrt
from typing import Union, Iterable, NoReturn, Dict, List, Any

from ..models import *
from django.db.models import Max, QuerySet
from .graffic import get_graph_data, get_graphics
from Field.models import Run


def add_anchor_point(data: dict) -> dict:
    """Добавить точку привзяки [Добавляем 0 в начало каждого переданного массива]"""
    try:
        if data['Глубина'][0] != 0:
            for key, lvalue in data.items():
                if key == "Рейс":
                    data[key] = [lvalue[0], *lvalue]
                elif key == "Комментарий":
                    data[key] = ['', *lvalue]
                else:
                    data[key] = [0, *lvalue]
    except IndexError:  # значит нет замеров
        pass
    return data


def get_data(runs: Union[object, Iterable[object]]) -> dict:
    """
    Функция для перезаписи даты в работу, опираясь на данные из бд.
    """
    if len(runs) == 0:  # передали не массив рейсов, а один рейс
        run = runs
        data = {'Статические замеры ИГИРГИ': IgirgiStatic.objects.filter(run=run),
                'Динамические замеры ННБ': DynamicNNBData.objects.filter(run=run),
                'Статические замеры ННБ': StaticNNBData.objects.filter(run=run),
                'Плановая траектория': Plan.objects.filter(run=run),
                'Динамические замеры ИГИРГИ': IgirgiDynamic.objects.filter(run=run),
                }
        if run.section.wellbore.igirgi_drilling:
            data['Плановая траектория интерп'] = InterpPlan.objects.filter(run=run)
    else:
        data = {'Статические замеры ИГИРГИ': IgirgiStatic.objects.filter(run__in=runs),
                'Динамические замеры ННБ': DynamicNNBData.objects.filter(run__in=runs),
                'Статические замеры ННБ': StaticNNBData.objects.filter(run__in=runs),
                'Плановая траектория': Plan.objects.filter(run__in=runs),
                'Динамические замеры ИГИРГИ': IgirgiDynamic.objects.filter(run__in=runs),
                }
        if runs[0].section.wellbore.igirgi_drilling:
            data['Плановая траектория интерп'] = InterpPlan.objects.filter(run__in=runs)

    del_key = list()
    # преобразуем queryset в словарь с листами (3 отдельных массива - Глубина, Угол, Азимут)
    for key, queryset in data.items():
        if len(queryset) != 0:
            meas_lists = {'Глубина': list(),
                          'Угол': list(),
                          'Азимут': list(),
                          }
            if key == 'Статические замеры ИГИРГИ':
                meas_lists['Комментарий'] = list()
                meas_lists['Рейс'] = list()

            for meas in queryset:
                meas_lists['Глубина'].append(meas.depth)
                meas_lists['Угол'].append(meas.corner)
                meas_lists['Азимут'].append(meas.azimut)
                if key == 'Статические замеры ИГИРГИ':
                    meas_lists['Рейс'].append(meas.run.run_number)
                    meas_lists['Комментарий'].append(meas.comment)
            data[key] = meas_lists
        else:
            del_key.append(key)  # удаляем те ключи у которых нет данных (например если нет динамических замеров)

    for key in del_key:
        data.pop(key)

    # добавим точку привязки, начальный 0

    add_anchor_point(data['Статические замеры ННБ'])
    add_anchor_point(data['Статические замеры ИГИРГИ'])
    add_anchor_point(data['Плановая траектория'])

    if data.get('Плановая траектория интерп') is not None:
        add_anchor_point(data['Плановая траектория интерп'])

    if data.get('Динамические замеры ННБ') is not None:
        add_anchor_point(data['Динамические замеры ННБ'])

    if data.get('Динамические замеры ИГИРГИ') is not None:
        add_anchor_point(data['Динамические замеры ИГИРГИ'])
    return data


def get_single_traj(dtype: str, wellbore: object) -> dict[list[int], list[int], list[int]] | None:
    """Делает то же самое что функция выше, но для одного типа замеров"""
    runs = Run.objects.filter(section__wellbore=wellbore)

    if dtype == 'staticIgirgi':
        queryset = IgirgiStatic.objects.filter(run__in=runs)
    if dtype == 'staticNNB':
        queryset = StaticNNBData.objects.filter(run__in=runs)
    if dtype == 'plan':
        queryset = Plan.objects.filter(run__in=runs)
    if dtype == 'dynamicIgirgi':
        queryset = IgirgiDynamic.objects.filter(run__in=runs)
    if dtype == 'dynamicNNB':
        queryset = DynamicNNBData.objects.filter(run__in=runs)

    data = {'Глубина': list(),
            'Угол': list(),
            'Азимут': list(), }
    for meas in queryset:
        data['Глубина'].append(meas.depth)
        data['Угол'].append(meas.corner)
        data['Азимут'].append(meas.azimut)

    if len(data['Глубина']) == 0:
        return None
    # добавим точку привязки, начальный 0
    if data['Глубина'][0] != 0:
        data['Глубина'] = [0, *data['Глубина']]
        data['Угол'] = [0, *data['Угол']]
        data['Азимут'] = [0, *data['Азимут']]
    return data


def last_depth(Wellbore: object):
    """ Получить последнюю точку замера cкважины"""
    return IgirgiStatic.objects.filter(run__section__wellbore=Wellbore).aggregate(Max('depth'))['depth__max']


def get_waste(my_wellbore):
    """По объекту ствола [ПАРАМЕТРЫ ОТХОДА]. Возвращает словарь слов (выше/ниже) и числами"""
    runs = Run.objects.filter(section__wellbore=my_wellbore)
    all_data = get_data(runs)
    return get_graphics(all_data, my_wellbore, only_waste=True)


def waste(wellbore: object, full: bool = False, dynamic: bool = False):
    """Возвращает численные значения отходов"""
    if dynamic:
        nnb = DynamicNNBData.objects.filter(run__section__wellbore=wellbore).order_by('depth')
        igirgi = IgirgiDynamic.objects.filter(run__section__wellbore=wellbore).order_by('depth')
    else:
        if wellbore.igirgi_drilling:  # если бурим по траектории ИГиРГИ то используем план вместо траектории ннб
            nnb = InterpPlan.objects.filter(run__section__wellbore=wellbore).order_by('depth')
        else:
            nnb = StaticNNBData.objects.filter(run__section__wellbore=wellbore).order_by('depth')
        igirgi = IgirgiStatic.objects.filter(run__section__wellbore=wellbore).order_by('depth')

    igirgi_data, nnb_data = {'Угол': list(), 'Азимут': list(), 'Глубина': list()}, \
        {'Угол': list(), 'Азимут': list(), 'Глубина': list()}

    for meas in nnb:
        nnb_data['Угол'].append(meas.corner)
        nnb_data['Азимут'].append(meas.azimut)
        nnb_data['Глубина'].append(meas.depth)

    for meas in igirgi:
        igirgi_data['Угол'].append(meas.corner)
        igirgi_data['Азимут'].append(meas.azimut)
        igirgi_data['Глубина'].append(meas.depth)

    add_anchor_point(igirgi_data)
    add_anchor_point(nnb_data)

    return calculation_waste(wellbore, igirgi_data, nnb_data, full)


def calculation_waste(wellbore: object, igirgi: dict, nnb: dict, full: bool = False) -> tuple[list | float,
                                                                                              list | float,
                                                                                              list | float]:
    """ Формируем отходы по последней точке
    Если full то выдает весь массив отходов"""

    RKB = (84 if wellbore.well_name.RKB is None else wellbore.well_name.RKB)
    VSaz = (1 if wellbore.well_name.VSaz is None else wellbore.well_name.VSaz)

    nnb_delta_x, nnb_delta_y, x2, y2, nnb_delta_TVD = get_graph_data(I=nnb['Угол'],
                                                                     A=nnb['Азимут'],
                                                                     Depth=nnb['Глубина'],
                                                                     RKB=RKB,
                                                                     VSaz=VSaz)

    igirgi_delta_x, igirgi_delta_y, x2, y2, igirgi_delta_TVD = get_graph_data(I=igirgi['Угол'],
                                                                              A=igirgi['Азимут'],
                                                                              Depth=igirgi['Глубина'],
                                                                              RKB=RKB,
                                                                              VSaz=VSaz)

    # пошли отходы
    Ex = (wellbore.well_name.EX if wellbore.well_name.EX is not None else 0)
    Ny = (wellbore.well_name.NY if wellbore.well_name.NY is not None else 0)

    if full:
        horiz = list()
        vert = list()
        departure = list()
        count = 0  # не выводим отходы для токи привязки
        for meas in zip(igirgi_delta_x, igirgi_delta_y, igirgi_delta_TVD, nnb_delta_x, nnb_delta_y, nnb_delta_TVD):
            if count == 0:
                count += 1
                continue

            X_nnb = Ex + meas[4]
            Y_nnb = Ny + meas[3]

            X_igirgi = Ex + meas[1]
            Y_igigri = Ny + meas[0]

            horiz.append(round(sqrt((X_nnb - X_igirgi) ** 2 + (Y_nnb - Y_igigri) ** 2), 2))
            vert.append(round(meas[5] - meas[2], 2))
            departure.append(
                round(sqrt((X_nnb - X_igirgi) ** 2 + (Y_nnb - Y_igigri) ** 2 + (meas[2] - meas[5]) ** 2), 2))
    else:
        X_nnb = nnb_delta_x[-1]
        X_igirgi = igirgi_delta_x[-1]
        Y_nnb = nnb_delta_y[-1]
        Y_igigri = igirgi_delta_y[-1]

        horiz = round(sqrt((X_nnb - X_igirgi) ** 2 + (Y_nnb - Y_igigri) ** 2), 2)  # отход по горизонтали
        vert = round(nnb_delta_TVD[-1] - igirgi_delta_TVD[-1], 2)  # отход по вертикали
        departure = round(
            sqrt((X_nnb - X_igirgi) ** 2 + (Y_nnb - Y_igigri) ** 2 + (nnb_delta_TVD[-1] - igirgi_delta_TVD[-1]) ** 2),
            2)  # отход общий
    return horiz, vert, departure


def clone_wellbore_traj(old_wellbore: object, new_wellbore: object) -> str:
    """Клонирование всех замеров старого ствола в новый ствол"""
    igirgi_list = list()
    nnb_list = list()
    for old_section in old_wellbore.sections.all():
        for old_run in old_section.runs.all():
            new_run = Run.objects.get(run_number=old_run.run_number, section__wellbore=new_wellbore)

            for meas in IgirgiStatic.objects.filter(run=old_run):
                igirgi_list.append(IgirgiStatic(run=new_run, depth=meas.depth, corner=meas.corner, azimut=meas.azimut,
                                                comment=meas.comment))

            for meas in StaticNNBData.objects.filter(run=old_run):
                nnb_list.append(StaticNNBData(run=new_run, depth=meas.depth, corner=meas.corner, azimut=meas.azimut))
    IgirgiStatic.objects.bulk_create(igirgi_list)
    StaticNNBData.objects.bulk_create(nnb_list)
    return 'Ok'


def intr_plan(run: object) -> QuerySet:
    """
    Провести интерполяцию плана по замерам ИГиРГИ
    Возвращает траекторию ИГиРГИ и интерполированный план
    """
    new_Indx = list()
    depth = list()
    azimut = list()
    corner = list()
    run_id = list()

    runs = Run.objects.filter(section__wellbore=run.section.wellbore)
    reference = IgirgiStatic.objects.filter(run__in=runs)
    old_interp = InterpPlan.objects.filter(run__in=runs)
    # записали все не интерполированные значения
    for ref in reference:
        if ref.depth not in [i.depth for i in old_interp]:
            new_Indx.append(ref.depth)
            run_id.append(ref.run.id)
    if len(new_Indx) != 0:
        for plan in Plan.objects.filter(run__in=runs):
            depth.append(plan.depth)
            azimut.append(plan.azimut)
            corner.append(plan.corner)

        for interp in zip(new_Indx, np.interp(new_Indx, depth, azimut), np.interp(new_Indx, depth, corner), run_id):
            InterpPlan.objects.create(depth=interp[0], azimut=round(interp[1], 2), corner=round(interp[2], 2),
                                      run_id=interp[3])
        old_interp = InterpPlan.objects.filter(run__in=runs)
    return reference, old_interp


from tqdm import tqdm


def NNBToIgirgi():
    """Переписывает комментарии из траектории ннб в игирги"""
    IgirgiStatic.objects.all()
    count = 0
    max_l = len(StaticNNBData.objects.all())
    warning_list = list()
    pbar = tqdm(total=max_l)

    for meas in StaticNNBData.objects.all():
        count += 1
        pbar.update(count)
        if meas.comment != '' or meas.comment is not None:
            try:
                obj = IgirgiStatic.objects.get(run_id=meas.run, depth=meas.depth)
                obj.comment = meas.comment
                obj.save()
            except Exception as e:
                warning = {'Рейс': meas.run,
                           'Глубина': meas.depth,
                           'Текст': meas.comment, }
                if warning['Текст'] != 'None' and warning['Текст'] != '' and warning['Текст'] is not None:
                    warning_list.append(warning)

    for war in warning_list:
        print(f"В рейсе:{war['Рейс']} Глубина:{war['Глубина']}; Текст:{war['Текст']};")
    return len(warning_list)
