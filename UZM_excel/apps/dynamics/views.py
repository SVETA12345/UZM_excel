from django.http import JsonResponse
from django.shortcuts import render, redirect

from Field.views_api import get_tree
from Field.models import Run

from report.models import IgirgiDynamic, DynamicNNBData

from report.function.model_service import waste


# Create your views here.


def dynamics_traj(request):
    """Страница для загрузки динамической траектории"""
    context = {'active': 'dynamics',
               'title': 'Динамическая траектория',
               "tree": get_tree(),
               }

    if request.GET.get('run_id') is not None:  # если в get запросе не run_id выводим пустую страницу
        run_id = request.GET.get('run_id')
        try:
            run = Run.objects.get(id=run_id)
            context['title'] = run.section.wellbore.well_name.get_title()
        except Run.DoesNotExist:  # если не нашли рейс возвращаем пустую страницу
            return render(request, 'data_handler/trajectories.html', {'context': context, })

        context['selected_obj'] = run  # для отображения текущей модели на странице (текст)
        # Замеры
        context["igirgi_data"] = IgirgiDynamic.objects.filter(run=run_id)
        context["nnb_data"] = DynamicNNBData.objects.filter(run=run_id)

        # Отходы
        context["waste_hor"], context["waste_ver"], context["waste_common"] = waste(run.section.wellbore, full=False,
                                                                                    dynamic=True)
        try:
            last_igirgi = IgirgiDynamic.objects.filter(run=run_id).latest('depth')
            last_nnb = DynamicNNBData.objects.filter(run=run_id).latest('depth')
            context['delta_depth'] = round(last_nnb.depth - last_igirgi.depth, 2)
            context['delta_corner'] = round(last_nnb.corner - last_igirgi.corner, 2)
            context['delta_azimut'] = round(last_nnb.azimut - last_igirgi.azimut, 2)
        except IgirgiDynamic.DoesNotExist:
            pass
        except DynamicNNBData.DoesNotExist:
            pass

    if request.method == 'POST':
        update_obj = list()
        create_obj = list()
        meas_str = request.POST['data'].replace(',', '.').replace('\r', '').split('\n')
        if request.POST.get("data-type") == 'Динамики ННБ':
            obj = DynamicNNBData
        else:
            obj = IgirgiDynamic
        for item in map(lambda x: x.split('\t'), meas_str):
            try:
                if item[0] != '' and item[1] != '' and item[2] != '':  # Если значения не нулевые
                    try:
                        new_meas = obj.objects.get(run=run, depth=float(item[0]))
                        new_meas.corner = float(item[1])
                        new_meas.azimut = float(item[2])
                        update_obj.append(new_meas)
                    except obj.DoesNotExist:
                        create_obj.append(
                            obj(run=run,
                                depth=float(item[0]),
                                corner=float(item[1]),
                                azimut=float(item[2]))
                        )
            except IndexError as e:
                print('Пропуск при вставке динамики', e)
            except ValueError as e:
                print('Пропуск при вставке динамики', e)
        obj.objects.bulk_create(create_obj)
        obj.objects.bulk_update(update_obj, ["corner", "azimut", ])
    print('CONTEXT', context)
    return render(request, 'dynamics/dynamic_trajectories.html', {'context': context, })


def edit_dynamics_traj(request):
    context = {'active': 'dynamics',
               'title': 'Динамическая траектория',
               "tree": get_tree(),
               }
    if request.GET.get('run_id') is not None:
        run_id = request.GET.get('run_id')
        run = Run.objects.get(id=request.GET.get('run_id'))
        context['title'] = run.section.wellbore.well_name.get_title()
        context['selected_obj'] = run
        context["igirgi_data"] = IgirgiDynamic.objects.filter(run=run_id)
        context["nnb_data"] = DynamicNNBData.objects.filter(run=run_id)

    if request.method == 'POST':
        for items in request.POST.lists():
            key = str(items[0]).split(' ')
            if 'nnb' in key:
                obj = DynamicNNBData.objects.get(id=key[0])
            else:
                obj = IgirgiDynamic.objects.get(id=key[0])
            if items[1][0] == '' or items[1][1] == '' or items[1][2] == '':
                obj.delete()
            else:
                obj.depth = float(items[1][0])
                obj.corner = float(items[1][1])
                obj.azimut = float(items[1][2])
                obj.save()
        return redirect('dynamics')

    return render(request, 'dynamics/dynamic_edit_trajectories.html', {'context': context, })


def del_dynamics(request):
    """Удаление замеров динамики"""
    for key, value in request.POST.dict().items():
        if 'igirgi' in key:
            IgirgiDynamic.objects.get(id=value).delete()
        elif 'nnb' in key:
            DynamicNNBData.objects.get(id=value).delete()
        else:
            continue
    return JsonResponse({'status': 'ok'})
