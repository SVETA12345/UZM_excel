from django.shortcuts import render, redirect

from Field.models import Well, Run, Wellbore, Section
from Field.views_api import get_tree
from Field.forms import AddWellForm, EditRunForm

from report.function.model_service import intr_plan, get_single_traj
from report.function.graffic import single_data_graph
from report.models import StaticNNBData, IgirgiStatic, Plan, InterpPlan, ProjectionParam
from report.function.operational_report.work_with_data import work_with_plan
from report.function.model_service import waste

from excel_parcer.models import Data

from .function.context_editer import *
from .function.mail import *


def index(request):
    """Главная страница"""
    return redirect(traj)


def traj(request):
    """Страница с траекторией ННБ и ИГиРГИ"""
    context = {"title": 'Траектория',
               "active": 'traj',
               "tree": get_tree(),
               }

    if request.method == "GET":
        if request.GET.get('run_id') is not None:  # если в get запросе не run_id выводим пустую страницу
            run_id = request.GET.get('run_id')
            try:
                run = Run.objects.get(id=run_id)
                context['title'] = run.section.wellbore.well_name.get_title()
            except Run.DoesNotExist:  # если не нашли рейс возвращаем пустую страницу
                return render(request, 'data_handler/trajectories.html', {'context': context, })

            context['selected_obj'] = run  # для отображения текущей модели на странице (текст)

            # Ищем план, формируем контекст для письма
            runs = Run.objects.filter(section__wellbore=run.section.wellbore).order_by('run_number')
            plan_data = Plan.objects.filter(run__in=runs)
            context["plan_ex"] = (True if len(plan_data) != 0 else False)
            context["plan_version"] = (plan_data[0].plan_version if context["plan_ex"] else '-')
            context['letter'] = Letter(run.section.wellbore)

            # Замеры
            context["igirgi_data"] = IgirgiStatic.objects.filter(run=run_id).exclude(depth=0)
            # БУРИМ ПО ПЛАНОВОЙ ТРАЕКТОРИИ
            if run.section.wellbore.igirgi_drilling:
                if context["plan_ex"]:
                    intr_plan(run)
                    context["nnb_data"] = InterpPlan.objects.filter(run=run_id).exclude(depth=0)
                else:
                    return render(request, 'data_handler/trajectories.html', {'context': context, })
            else:
                context["nnb_data"] = StaticNNBData.objects.filter(run=run_id).exclude(depth=0)

            try:
                # Последний замер прошлого рейса (Ближайший замер)
                for i, r in enumerate(runs):
                    if run == r and run != runs[0]:
                        context["previous_igirgi_meas"] = IgirgiStatic.objects.filter(run=runs[i-1]).latest('depth')
                        objs = InterpPlan if run.section.wellbore.igirgi_drilling else StaticNNBData
                        context["previous_nnb_meas"] = objs.objects.filter(run=runs[i - 1]).latest('depth')

                # Отходы
                context["waste_hor"], context["waste_vert"], context["waste_common"] = waste(run.section.wellbore, True)
                # Индексы отходов (Какие отходы выводить)
                context["waste_index"] = list()
                for ind, data in enumerate(IgirgiStatic.objects.filter(
                        run__section__wellbore=run.section.wellbore).exclude(depth=0).order_by('depth')):
                    if run.section.wellbore.igirgi_drilling:
                        if data in context['igirgi_data'] and ind < len(InterpPlan.objects.filter(
                                run__section__wellbore=run.section.wellbore).exclude(depth=0).order_by('depth')):
                            context["waste_index"].append(ind)
                    else:
                        if data in context['igirgi_data'] and ind < len(StaticNNBData.objects.filter(
                                run__section__wellbore=run.section.wellbore).exclude(depth=0).order_by('depth')):
                            context["waste_index"].append(ind)
                try:
                    context["waste_index_0"] = context["waste_index"][0]-1
                except IndexError:
                    context["waste_index_0"] = 0
            except IgirgiStatic.DoesNotExist:
                pass
            except StaticNNBData.DoesNotExist:
                pass

    if request.method == 'POST':
        run = Run.objects.get(id=request.GET.get('run_id'))
        context['title'] = run.section.wellbore.well_name.get_title()

        if 'plan_depth' in request.POST:  # данные с модальной формы 2 (плановая траектория)
            work_with_plan(request, run)

        if 'data-depth' in request.POST:  # данные с модальной формы 1 (добавление значений)
            depth_data = request.POST['data-depth'].replace(',', '.').replace(' ', '') \
                .replace('\r', '').replace('\n', '\t').split('\t')
            corner_data = request.POST['data-corner'].replace(',', '.').replace(' ', '') \
                .replace('\r', '').replace('\n', '\t').split('\t')
            azimut_data = request.POST['data-azimut'].replace(',', '.').replace(' ', '') \
                .replace('\r', '').replace('\n', '\t').split('\t')

            if request.POST.get("data-type") == 'ННБ':
                obj = StaticNNBData.objects
            else:
                obj = IgirgiStatic.objects
            for meas in zip(depth_data, corner_data, azimut_data):
                if meas[0] != '' and meas[1] != '' and meas[2] != '':  # Если значения не нулевые
                    new_obj = obj.get_or_create(run=run, depth=meas[0])
                    new_obj[0].corner = meas[1]
                    new_obj[0].azimut = meas[2]
                    new_obj[0].save()

        return redirect(request.META.get('HTTP_REFERER'))  # вернуть на ту же страницу, где и были
    return render(request, 'data_handler/trajectories.html', {'context': context, })


def edit_traj(request):
    """Страница с редактированием траекторией ННБ и ИГиРГИ"""
    context = {"title": 'Траектория',
               "active": 'traj',
               "tree": get_tree(),
               }

    run_id = request.GET.get('run_id')
    run = Run.objects.get(id=request.GET.get('run_id'))
    context['title'] = run.section.wellbore.well_name.get_title()
    context['selected_obj'] = run
    context["igirgi_data"] = IgirgiStatic.objects.filter(run=run_id)
    if run.section.wellbore.igirgi_drilling:
        context["nnb_data"] = InterpPlan.objects.filter(run=run_id)
    else:
        context["nnb_data"] = StaticNNBData.objects.filter(run=run_id)

    if request.method == 'POST':
        for items in request.POST.lists():
            key = str(items[0]).split(' ')
            if 'nnb' in key:
                if run.section.wellbore.igirgi_drilling:
                    obj = InterpPlan.objects.get(id=key[0])
                else:
                    obj = StaticNNBData.objects.get(id=key[0])
            else:
                obj = IgirgiStatic.objects.get(id=key[0])
            # print(items[1])  # - все 3 числа замеров
            if items[1][0] == '' or items[1][1] == '' or items[1][2] == '':
                obj.delete()
            else:
                obj.depth = float(items[1][0])
                obj.corner = float(items[1][1])
                obj.azimut = float(items[1][2])
                obj.save()

        return redirect('traj')
    return render(request, 'data_handler/edit_trajectories.html', {'context': context, })


def param(request):
    """Страница с параметрами скважины, сводкой и клонированием ствола"""
    context = {"title": 'Параметры',
               "active": 'param',
               "tree": get_tree(),
               'cards': list(),  # карточки стволов
               }

    if request.GET.get('run_id') is not None:
        try:  # если не нашли рейс отображаем пустую страницу
            run = Run.objects.get(id=request.GET.get('run_id'))
            context['title'] = run.section.wellbore.well_name.get_title()
        except Run.DoesNotExist:
            context['form'] = AddWellForm()
            return render(request, 'data_handler/param.html', {'context': context, })
        # сводка
        context['summary'] = run.section.wellbore.well_name.summary.all().order_by('-time')
        # для работы со стволами
        context["wellbore_choices"] = run.section.wellbore.get_choices()
        context['selected_obj'] = run.section.wellbore.well_name
        # карточки со стволами
        for wellbore in Wellbore.objects.filter(well_name=run.section.wellbore.well_name):
            context['cards'].append(WellboreCard(wellbore))
    else:
        context['form'] = AddWellForm(request.POST)
        return render(request, 'data_handler/param.html', {'context': context, })

    context['form'] = AddWellForm(instance=run.section.wellbore.well_name)

    if request.method == 'POST':
        context['form'] = AddWellForm(request.POST, instance=run.section.wellbore.well_name)
        context['form'].mail_replace()
        if context['form'].is_valid():
            context['form'].save()
        else:
            print(context['form'].errors.as_data())

    return render(request, 'data_handler/param.html', {'context': context, })


def run_param(request):
    """Страница с параметрами рейса"""
    context = {"title": 'Параметры рейса',
               "active": 'run',
               "tree": get_tree(),
               }

    if request.GET.get('run_id') is not None:
        try:  # если не нашли рейс отображаем пустую страницу
            run = Run.objects.get(id=request.GET.get('run_id'))
            context['selected_obj'] = run
            context['form'] = EditRunForm(instance=run)
        except Run.DoesNotExist:
            context['form'] = EditRunForm()
            return render(request, 'data_handler/run_param.html', {'context': context, })
    else:
        context['form'] = EditRunForm()
        return render(request, 'data_handler/run_param.html', {'context': context, })

    if request.method == 'POST':
        context['form'] = EditRunForm(request.POST, instance=run)
        if context['form'].is_valid():
            context['form'].save()
            print('сохранили')
        else:
            print('Ошибка изменения параметров =', context['form'].errors.as_data())

    return render(request, 'data_handler/run_param.html', {'context': context, })


def plan(request):
    """ Страница с плановой траекторией """
    context = {'title': 'Плановая траектория',
               "tree": get_tree(),
               "active": 'plan', }

    if request.GET.get('run_id') is not None:
        try:  # проверка на существование рейса
            run = Run.objects.get(id=request.GET.get('run_id'))
            context['title'] = run.section.wellbore.well_name.get_title()
        except:
            return render(request, 'data_handler/plan.html', {'context': context, })
        context['selected_obj'] = run

        # ищем план в БД
        for section in run.section.wellbore.sections.all():
            runs = section.runs.all()
            plan_meas = Plan.objects.filter(run__in=runs)
            if len(plan_meas) != 0:
                context['plan'] = plan_meas
                context["plan_ex"] = True
                context["plan_version"] = (Plan.objects.filter(run__in=runs)[0].plan_version if context["plan_ex"] else
                                           '-')
                break

    if request.method == 'POST':
        if 'plan_depth' in request.POST:  # данные с модальной формы 2 (плановая траектория)
            work_with_plan(request, run)

    return render(request, 'data_handler/plan.html', {'context': context, })


def proj(request):
    """ Страница с проекциями """
    context = {'title': 'Проекция',
               "tree": get_tree(),
               "active": 'proj',
               "data": {'staticIgirgi': {'hor': list(), 'ver': list()},
                        'staticNNB': {'hor': list(), 'ver': list()},
                        'plan': {'hor': list(), 'ver': list()},
                        'dynamicIgirgi': {'hor': list(), 'ver': list()},
                        'dynamicNNB': {'hor': list(), 'ver': list()},}
               }

    if request.GET.get('run_id') is not None:
        run = Run.objects.get(id=request.GET.get('run_id'))
        context['selected_obj'] = run.section.wellbore
        context['graph_param'] = ProjectionParam.objects.get_or_create(wellbore=context['selected_obj'])[0]
        # данные для проекции
        for key, vdict in list(context["data"].items()):
            dtraj = get_single_traj(key, context['selected_obj'])  # получаем траекторию в словаре
            if dtraj is None:
                context["data"].pop(key)
                continue
            # получаем проекцию
            x1, y1, x2, y2, z = single_data_graph(dtraj, context['selected_obj'])
            for meas in zip(x1, y1):
                vdict['hor'].append({'x': meas[0], 'y': meas[1]})

            for meas in zip(x2, y2):
                vdict['ver'].append({'x': meas[0], 'y': meas[1]})

    return render(request, 'data_handler/proj.html', {'context': context, })


class WellboreCard:
    """ Класс карточек для отображения на странице параметров"""
    def __init__(self, wellbore):
        self.obj = wellbore
        self.id = wellbore.id
        self.title = wellbore.get_full_wellbore_name
        runs = Run.objects.filter(section__wellbore=wellbore)
        self.section_len = Section.objects.filter(wellbore=wellbore).count()
        self.igirgi_len = IgirgiStatic.objects.filter(run__in=runs).count()
        self.nnb_len = StaticNNBData.objects.filter(run__in=runs).count()
