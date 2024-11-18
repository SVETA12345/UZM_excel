import copy
import math
import os
from math import sin, cos
from typing import Tuple, Any, Dict

from PIL import Image, ImageDraw, ImageFont
from random import random, randint

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from ..models import ProjectionParam

file_dir = os.getcwd() + "\\Files"


def getGorizontalAxes(Inc1, Inc2, Az1, Az2, deltaMD):
    """
    Получаем шаг по X, Y, Z для горизонтальной проекции
    """
    # print(f'DeltaMd = {deltaMD}, deltaInc = {Inc1}-{Inc2}')
    dInc = math.radians(Inc2 - Inc1)
    dAzim = math.radians(Az2 - Az1)
    I1 = math.radians(Inc1)
    I2 = math.radians(Inc2)
    A1 = math.radians(Az1)
    A2 = math.radians(Az2)

    beta = math.acos(cos(dInc) - sin(I1) * sin(I2) * (1 - cos(dAzim)))
    # beta = (1 if beta == 0 else beta)
    RF = (2 / beta) * math.tan(beta / 2) if beta != 0 else 1

    deltaX = (deltaMD / 2) * (sin(I1) * cos(A1) + sin(I2) * cos(A2)) * RF
    deltaY = (deltaMD / 2) * (sin(I1) * sin(A1) + sin(I2) * sin(A2)) * RF
    deltaZ = (deltaMD / 2) * (cos(I1) + cos(I2)) * RF

    # print("beta ", beta, " RF ", RF, ' deltaTVD ', deltaZ, 'deltaNS ', deltaX, ' deltaEW ', deltaY)
    return deltaX, deltaY, deltaZ


def getVerticalAxes(NS2: int, EW2: int, VSaz: int) -> tuple[float, float]:
    """
        Получаем шаг по Vsect2, ClsDisp2 для вертикальной проекции
        """

    ClsDisp2 = math.sqrt(NS2 ** 2 + EW2 ** 2)

    if ClsDisp2 == 0:
        ClsAz2 = 0
    elif NS2 < 0:
        ClsAz2 = math.atan(EW2 / NS2) * 180 / math.pi + 180
    else:
        ClsAz2 = math.atan(EW2 / NS2) * 180 / math.pi

    # print(f'NS: {NS2} | EW: {EW2} | ClsAz2: {ClsAz2}')
    delta_for_cos = (ClsAz2 - VSaz) * math.pi / 180
    Vsect2 = cos(delta_for_cos) * ClsDisp2
    # print(f"VSaz: {VSaz} |  ClsDisp: {ClsDisp2} | ClsAz2: {ClsAz2} | Vsect: {Vsect2} ")
    return Vsect2, ClsDisp2


def get_graph_data(I: list, A: list, Depth: list, RKB: int = 84, VSaz: int = 1) -> list:
    """
    I - угол
    А - азимут
    Depth - глубина
    RKB - высота ствола ротора (параметры скважины)
    VSaz - азимут вертикальной секции (параметры скважины)
    Здесь получаем данные для постройки горизонтальной и вертикальной проекции
    EW_list - запад/восток,
    NS_list - север/юг,
    Vsect_list, TVDSS_list, TVD_list

    Возвращает данные в порядке EW_list, NS_list, Vsect_list, TVDSS_list, TVD_list
    """
    TVD = 0
    TVDSS = RKB
    Vsect = 0
    NS = 0
    EW = 0

    ClsDisp = 0
    NS_list: list() = [0, ]
    EW_list: list() = [0, ]
    Vsect_list: list() = [0, ]
    TVDSS_list: list() = [RKB, ]
    TVD_list: list() = [0, ]

    all_measurement = list(zip(Depth, I, A))
    # print('-----------------------')
    for i, meas in enumerate(all_measurement):
        if meas[0] == all_measurement[-1][0]:
            # print(f'break - {all_measurement[-1][0]}')
            break
        # print(meas[0])
        deltaNS, deltaEW, deltaTVD = getGorizontalAxes(Inc1=meas[1],
                                                       Inc2=all_measurement[i + 1][1],
                                                       Az1=meas[2],
                                                       Az2=all_measurement[i + 1][2],
                                                       deltaMD=(all_measurement[i + 1][0] - meas[0]))
        # print(f'Vsect {Vsect} | TVD {TVD} | TVDSS {TVDSS}')

        # print(f"delta: {deltaNS, deltaEW, deltaTVD}")

        NS += deltaNS
        EW += deltaEW
        TVD += deltaTVD
        TVDSS -= deltaTVD  # TVD

        Vsect, ClsDisp = getVerticalAxes(NS2=NS,
                                         EW2=EW,
                                         VSaz=VSaz)
        # print('Depth ', all_measurement[i + 1][0], ' NS ', NS, ' EW ', EW)
        NS_list.append(NS)
        EW_list.append(EW)
        Vsect_list.append(Vsect)
        TVD_list.append(TVD)
        TVDSS_list.append(TVDSS)
    return EW_list, NS_list, Vsect_list, TVDSS_list, TVD_list


data_name = {'igirgi_file': 'Статические замеры ИГИРГИ',
             'nnb_dynamic': 'Динамические замеры ННБ',
             'nnb_static': 'Статические замеры ННБ',
             'raw_file': 'Сырые динамические замеры',
             'plan_traj_file': 'Плановая траектория',
             'igirgi_dynamic': 'Динамические замеры ИГИРГИ',
             }


# TODO получаем QueryDict и преобразовываем в словарь листов
def single_data_graph(data, wellbore: object) -> tuple[Any, Any, Any, Any, Any]:
    """ Значения для графиков проекции одиночные (берём индивидуально под тип траектории)"""
    well = wellbore.well_name
    # для траектории
    RKB = (84 if well.RKB is None else well.RKB)
    VSaz = (1 if well.VSaz is None else well.VSaz)
    x1, y1, x2, y2, z = get_graph_data(I=data['Угол'],
                                       A=data['Азимут'],
                                       Depth=data['Глубина'],
                                       RKB=RKB,
                                       VSaz=VSaz)
    return x1, y1, x2, y2, z


def get_graphics(all_data: dict, wellbore: object, only_waste: bool = False) -> tuple[dict, dict]:
    """
    Строит график, сохраняет его в /Report_out/1.png
    На выходе словарь с данными для записи в эксель и наименование при отходах
    Ключи в словаре:
            -nnb_delta_y
            -nnb_delta_x
            -nnb_TVD
            -igirgi_TVDSS
            -igirgi_delta_y
            -igirgi_delta_x
            -igirgi_TVD
    """


    well = wellbore.well_name
    data_dict = dict()  # словарь с данными, которые необходимо записать в эксель

    # Константы
    # для траектории
    RKB = (84 if well.RKB is None else well.RKB)
    VSaz = (1 if well.VSaz is None else well.VSaz)

    # для отходов
    Ex = (well.EX if well.EX is not None else 0)
    Ny = (well.NY if well.NY is not None else 0)

    fig = plt.figure(figsize=(15, 15))
    ax1 = fig.add_subplot(2, 2, 1)
    ax2 = fig.add_subplot(2, 2, 2)
    fig.subplots_adjust(wspace=0.5, hspace=0.5)

    data = all_data['Плановая траектория']
    x1, y1, x2, y2, z = get_graph_data(I=data['Угол'],
                                       A=data['Азимут'],
                                       Depth=data['Глубина'],
                                       RKB=RKB,
                                       VSaz=VSaz)

    ext_dict = {'min_x': min(x1),  # для границ графика
                'max_x': max(x1),
                'min_y': min(y1),
                'max_y': max(y1)}

    ax1.plot(x1, y1, 'g', label='Плановая траектория')
    ax2.plot(x2, y2, 'g', label='Плановая траектория')

    if wellbore.igirgi_drilling:  # подмена отходов при бурении на основе плана
        data = all_data['Плановая траектория интерп']
        x1, y1, x2, y2, z = get_graph_data(I=data['Угол'],
                                           A=data['Азимут'],
                                           Depth=data['Глубина'],
                                           RKB=RKB,
                                           VSaz=VSaz)

        data_dict['nnb_TVD'] = copy.deepcopy(z)
        data_dict['nnb_TVDSS'] = copy.deepcopy(y2)
        data_dict['nnb_delta_y'] = copy.deepcopy(y1)
        data_dict['nnb_delta_x'] = copy.deepcopy(x1)

    data = all_data['Статические замеры ННБ']
    x1, y1, x2, y2, z = get_graph_data(I=data['Угол'],
                                       A=data['Азимут'],
                                       Depth=data['Глубина'],
                                       RKB=RKB,
                                       VSaz=VSaz)
    # ext_list.extend([min(x1), max(x1), min(y1), max(y1)])
    ax1.plot(x1, y1, 'b', label='Подрядчик по ННБ')
    ax2.plot(x2, y2, 'b', label='Подрядчик по ННБ')

    if not wellbore.igirgi_drilling:
        X_nnb = x1[-1]  # EW для отходов
        Y_nnb = y1[-1]  # NS для отходов
        data_dict['nnb_TVD'] = copy.deepcopy(z)
        data_dict['nnb_TVDSS'] = copy.deepcopy(y2)
        data_dict['nnb_delta_y'] = copy.deepcopy(y1)
        data_dict['nnb_delta_x'] = copy.deepcopy(x1)

    data = all_data['Статические замеры ИГИРГИ']
    x1, y1, x2, y2, z = get_graph_data(I=data['Угол'],
                                       A=data['Азимут'],
                                       Depth=data['Глубина'],
                                       RKB=RKB,
                                       VSaz=VSaz)

    ax1.plot(x1, y1, color='orange', label='IGIRGI')
    ax2.plot(x2, y2, color='orange', label='IGIRGI')
    # for item in zip(x1, y1, x2, y2, z, data['Глубина']): print(f"NS: {item[0]} | EW: {item[1]} | Vsect: {item[2]} |
    # TVDSS: {item[3]} | TVD: {item[4]} | DEPTH: {item[5]}")

    data_dict['igirgi_TVD'] = copy.deepcopy(z)
    data_dict['igirgi_TVDSS'] = copy.deepcopy(y2)
    data_dict['igirgi_delta_y'] = copy.deepcopy(y1)
    data_dict['igirgi_delta_x'] = copy.deepcopy(x1)

    if 'Динамические замеры ННБ' in all_data.keys():
        data = all_data['Динамические замеры ННБ']
        x1, y1, x2, y2, z = get_graph_data(I=data['Угол'],
                                           A=data['Азимут'],
                                           Depth=data['Глубина'],
                                           RKB=RKB,
                                           VSaz=VSaz)
        ax2.plot(x2, y2, 'b--', label='ННБ_Din')

        data_dict['dynamic_nnb_TVD'] = copy.deepcopy(z)
        data_dict['dynamic_nnb_TVDSS'] = copy.deepcopy(y2)
        data_dict['dynamic_nnb_delta_y'] = copy.deepcopy(y1)
        data_dict['dynamic_nnb_delta_x'] = copy.deepcopy(x1)

    if 'Динамические замеры ИГИРГИ' in all_data.keys():
        data = all_data['Динамические замеры ИГИРГИ']
        # print(all_data['Динамические замеры ИГИРГИ'])
        x1, y1, x2, y2, z = get_graph_data(I=data['Угол'],
                                           A=data['Азимут'],
                                           Depth=data['Глубина'],
                                           RKB=RKB,
                                           VSaz=VSaz)
        ax2.plot(x2, y2, '--', color='orange', label='IGIRGI_Din')

        data_dict['dynamic_igirgi_TVD'] = copy.deepcopy(z)
        data_dict['dynamic_igirgi_TVDSS'] = copy.deepcopy(y2)
        data_dict['dynamic_igirgi_delta_y'] = copy.deepcopy(y1)
        data_dict['dynamic_igirgi_delta_x'] = copy.deepcopy(x1)

    # собственные границы графиков
    step = 6  # на графике 6 шагов
    delta_x = (ext_dict['max_x'] - ext_dict['min_x'])
    delta_y = (ext_dict['max_y'] - ext_dict['min_y'])

    if delta_x > delta_y:
        ext_dict['max_y'] += (delta_x - delta_y) / 2
        ext_dict['min_y'] -= (delta_x - delta_y) / 2
        additional_delta = delta_x / (step * 2)
    else:
        ext_dict['max_x'] += (delta_y - delta_x) / 2
        ext_dict['min_x'] -= (delta_y - delta_x) / 2
        additional_delta = delta_y / (step * 2)

    # строим график по заданным границам, если они есть
    try:
        graph_param = ProjectionParam.objects.get(wellbore=wellbore)
    except ProjectionParam.DoesNotExist:
        graph_param = None

    if graph_param is not None:
        if None not in (graph_param.hor_x_min, graph_param.hor_x_max):
            ax1.set_xlim(graph_param.hor_x_min, graph_param.hor_x_max)
            ax1.set_xticks(np.arange(graph_param.hor_x_min, graph_param.hor_x_max, graph_param.hor_x_del))
        else:
            ax1.set_xlim(ext_dict['min_x'] - additional_delta, ext_dict['max_x'] + additional_delta)
        if None not in (graph_param.hor_y_min, graph_param.hor_y_max):
            ax1.set_ylim(graph_param.hor_y_min, graph_param.hor_y_max)
            ax1.set_yticks(np.arange(graph_param.hor_y_min, graph_param.hor_y_max, graph_param.hor_y_del))
        else:
            ax1.set_ylim(ext_dict['min_y'] - additional_delta, ext_dict['max_y'] + additional_delta)

        if None not in (graph_param.ver_x_min, graph_param.ver_x_max):
            ax2.set_xlim(graph_param.ver_x_min, graph_param.ver_x_max)
            ax2.set_xticks(np.arange(graph_param.ver_x_min, graph_param.ver_x_max, graph_param.ver_x_del))

        if None not in (graph_param.ver_y_min, graph_param.ver_y_max):
            ax2.set_ylim(graph_param.ver_y_min, graph_param.ver_y_max)
            ax2.set_yticks(np.arange(graph_param.ver_y_min, graph_param.ver_y_max, graph_param.ver_y_del))
    else:
        # создаем квадратную сетку
        ax1.set_xlim(ext_dict['min_x'] - additional_delta, ext_dict['max_x'] + additional_delta)
        ax1.set_ylim(ext_dict['min_y'] - additional_delta, ext_dict['max_y'] + additional_delta)

    ax1.set_xlabel('Запад/Восток')
    ax1.set_ylabel('Юг/Север')
    ax1.set_title('Горизонтальная проекция')
    # ax1.legend(title='Горизонтальная проекция', loc=(0, -0.4), mode='expand', ncols=1)
    ax1.grid()
    ax2.set_xlabel('Вертикальная секция')
    ax2.set_ylabel('Абсолютная отметка')
    ax2.set_title('Вертикальная проекция')
    # ax2.legend(title='Вертикальная проекция', bbox_to_anchor=(0.85, -0.15))
    ax2.grid()

    ax2.legend(bbox_to_anchor=(-0.015, -0.15), fontsize=10)  # общая подпись

    # сохраняем изображение
    plt.savefig(file_dir + f'/Report_out/{wellbore}.png')

    # Числовые и словесные значения отходов последней точки
    number_data, waste_word = get_number_data(data_dict, all_data)

    if 'Динамические замеры ИГИРГИ' in all_data:
        number_data2, waste_word2 = get_number_data(data_dict, all_data, dynamic=True)

    # вставка текста на изображение
    image = Image.open(file_dir + f'/Report_out/{wellbore}.png')
    font = ImageFont.truetype("arial.ttf", 25)
    drawer = ImageDraw.Draw(image)
    if 'Динамические замеры ИГИРГИ' in all_data:
        drawer.text((180, 850),
                    f'Статические замеры\n\n'
                    f'Точка замера: {format(number_data["Точка замера"], ".2f")} м\n'
                    f'Отход по горизонтали: {format(number_data["Отход по горизонтали"], ".2f")} м {waste_word["hor"]}\n'
                    f'Отход по вертикали: {format(number_data["Отход по вертикали"], ".2f")} м {waste_word["ver"]}\n'
                    f'Общий отход: {format(number_data["Общий отход"], ".2f")} м\n'
                    f'Абсолютная отметка: {format(number_data["Абсолютная отметка"], ".2f")} м\n',
                    font=font, fill='black')
        drawer.text((880, 850),
                    f'Динамические замеры\n\n'
                    f'Точка замера: {format(number_data2["Точка замера"], ".2f")} м\n'
                    f'Отход по вертикали: {format(number_data2["Отход по вертикали"], ".2f")} м {waste_word2["ver"]}\n'
                    f'Абсолютная отметка: {format(number_data2["Абсолютная отметка"], ".2f")} м\n',
                    font=font, fill='black')
    else:
        drawer.text((180, 850),
                    f'Точка замера: {format(number_data["Точка замера"], ".2f")} м\n'
                    f'Отход по горизонтали: {format(number_data["Отход по горизонтали"], ".2f")} м {waste_word["hor"]}\n'
                    f'Отход по вертикали: {format(number_data["Отход по вертикали"], ".2f")} м {waste_word["ver"]}\n'
                    f'Общий отход: {format(number_data["Общий отход"], ".2f")} м\n'
                    f'Абсолютная отметка: {format(number_data["Абсолютная отметка"], ".2f")} м\n',
                    font=font, fill='black')
    image.save(file_dir + f'/Report_out/{wellbore}.png')

    if only_waste:
        return number_data, waste_word

    # для отображения в письме добавляем ()
    waste_word["hor"] = ('(' + waste_word["hor"] + ')' if waste_word["hor"] != '' else waste_word["hor"])
    waste_word["ver"] = ('(' + waste_word["ver"] + ')' if waste_word["ver"] != '' else waste_word["ver"])

    return data_dict, waste_word


def get_number_data(data_dict: dict, all_data: dict, dynamic: bool = False) -> tuple[dict, dict]:
    """Формируем данные для текста на графике [ПАРАМЕТРЫ ОТХОДА]"""
    number_data = dict()
    if dynamic:
        number_data['Точка замера'] = all_data['Динамические замеры для графика']['depths']['igirgi']
        X_nnb = data_dict['dynamic_nnb_delta_x'][-1]  # EW для отходов
        Y_nnb = data_dict['dynamic_nnb_delta_y'][-1]  # NS для отходов
        X_igirgi = data_dict['dynamic_igirgi_delta_x'][-1]  # EW для отходов
        Y_igigri = data_dict['dynamic_igirgi_delta_y'][-1]  # NS для отходов
        number_data['Абсолютная отметка'] = round(data_dict['dynamic_igirgi_TVDSS'][-1], 2)
        number_data['Отход по вертикали'] = all_data['Динамические замеры для графика']['wastes'][1]
    else:
        number_data['Точка замера'] = all_data['Статические замеры ИГИРГИ']['Глубина'][-1]
        X_nnb = data_dict['nnb_delta_x'][-1]  # EW для отходов
        Y_nnb = data_dict['nnb_delta_y'][-1]  # NS для отходов
        X_igirgi = data_dict['igirgi_delta_x'][-1]  # EW для отходов
        Y_igigri = data_dict['igirgi_delta_y'][-1]  # NS для отходов
        number_data['Абсолютная отметка'] = round(data_dict['igirgi_TVDSS'][-1], 2)
        number_data['Отход по вертикали'] = round(data_dict['nnb_TVD'][-1] - data_dict['igirgi_TVD'][-1], 2)

    number_data['Отход по горизонтали'] = round(math.sqrt((X_nnb - X_igirgi) ** 2 + (Y_nnb - Y_igigri) ** 2), 2)

    # при 0 убираем знак в названии
    number_data['Отход по горизонтали'] = (
        number_data['Отход по горизонтали'] if number_data['Отход по горизонтали'] != 0.0
        else abs(number_data['Отход по горизонтали']))
    number_data['Отход по вертикали'] = (
        number_data['Отход по вертикали'] if number_data['Отход по вертикали'] != 0.0
        else abs(number_data['Отход по вертикали']))
    number_data['Общий отход'] = round(
        math.sqrt((X_nnb - X_igirgi) ** 2 + (Y_nnb - Y_igigri) ** 2 + (
                data_dict['nnb_TVD'][-1] - data_dict['igirgi_TVD'][-1]) ** 2), 2)

    # Ключевые слова отходов для письма и для отчёта
    waste_word = dict()
    AZ = all_data['Статические замеры ННБ']['Азимут'][-1]  # по горизонтали

    if 45 <= AZ <= 135:
        if Y_igigri == Y_nnb:
            waste_word['hor'] = ''
        else:
            waste_word['hor'] = ('правее' if Y_igigri < Y_nnb else 'левее')
    elif 225 <= AZ <= 315:
        if Y_igigri == Y_nnb:
            waste_word['hor'] = ''
        else:
            waste_word['hor'] = ('правее' if Y_igigri > Y_nnb else 'левее')
    elif 135 <= AZ <= 225:
        if X_igirgi == X_nnb:
            waste_word['hor'] = ''
        else:
            waste_word['hor'] = ('правее' if X_igirgi < X_nnb else 'левее')
    elif AZ >= 315 or AZ <= 45:
        if X_igirgi == X_nnb:
            waste_word['hor'] = ''
        else:
            waste_word['hor'] = ('правее' if X_igirgi > X_nnb else 'левее')

    if number_data["Отход по вертикали"] == 0:  # по вертикали
        waste_word['ver'] = ''
    else:
        waste_word['ver'] = ('выше' if number_data["Отход по вертикали"] > 0 else 'ниже')

    return number_data, waste_word

