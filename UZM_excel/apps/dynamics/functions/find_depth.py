from report.models import IgirgiDynamic, DynamicNNBData


def find_depths(run_id: int = None, runs=None):
    '''
    функция возращает подходящую глубину(по которой в дальнейшем считаем отходы и азимут) в разделе динамика
    '''
    context = {'depths':{}}
    try:
        if run_id:
            all_igirgi = IgirgiDynamic.objects.filter(run=run_id).order_by('depth')
            all_nnb = DynamicNNBData.objects.filter(run=run_id).order_by('depth')
            if len(list(all_igirgi))>0 and len(list(all_nnb)) > 0:
                last_igirgi = list(all_igirgi)[-1]
                last_nnb = list(all_nnb)[-1]
                max_depth = min(last_igirgi.depth, last_nnb.depth)
                last_igirgi = IgirgiDynamic.objects.filter(run=run_id, depth=max_depth).latest('depth')
                last_nnb = DynamicNNBData.objects.filter(run=run_id, depth=max_depth).latest('depth')
                context['delta_depth'] = max_depth
                context['delta_corner'] = round(last_nnb.corner - last_igirgi.corner, 2)
                context['delta_azimut'] = round(last_nnb.azimut - last_igirgi.azimut, 2)
                # необходимо для подсветки зелёным цветом
                context['depths'] = {'nnb': max_depth, 'igirgi': max_depth}
        else:
            all_igirgi = IgirgiDynamic.objects.filter(run__in=runs).order_by('depth')
            all_nnb = DynamicNNBData.objects.filter(run__in=runs).order_by('depth')
            if len(list(all_igirgi)) > 0 and len(list(all_nnb)) > 0:
                print('blet')
                last_igirgi = list(all_igirgi)[-1]
                last_nnb = list(all_nnb)[-1]
                max_depth = min(last_igirgi.depth, last_nnb.depth)
                last_igirgi = IgirgiDynamic.objects.filter(run__in=runs, depth=max_depth).latest('depth')
                last_nnb = DynamicNNBData.objects.filter(run__in=runs, depth=max_depth).latest('depth')
                context['delta_depth'] = max_depth
                context['delta_corner'] = round(last_nnb.corner - last_igirgi.corner, 2)
                context['delta_azimut'] = round(last_nnb.azimut - last_igirgi.azimut, 2)
                # необходимо для подсветки зелёным цветом
                context['depths'] = {'nnb': max_depth, 'igirgi': max_depth}
    except IgirgiDynamic.DoesNotExist:
        # ищем максимально приближённый по глубине элемент
        min_dif = 10000
        last_igirgi = None
        for elem in all_igirgi:
            if abs(elem.depth - max_depth) <= 0.5 and min_dif > abs(elem.depth - max_depth):
                min_dif = abs(elem.depth - max_depth)
                last_igirgi = elem
        # если подходядщая глубина найдена
        if last_igirgi:
            context['delta_depth'] = max_depth
            context['delta_corner'] = round(last_nnb.corner - last_igirgi.corner, 2)
            context['delta_azimut'] = round(last_nnb.azimut - last_igirgi.azimut, 2)
            context['depths'] = {'nnb': max_depth, 'igirgi': last_igirgi.depth}
    except DynamicNNBData.DoesNotExist:
        # ищем максимально приближённый по глубине элемент
        min_dif = 10000
        last_nnb = None
        for elem in all_nnb:
            if abs(elem.depth - max_depth) <= 0.5 and min_dif > abs(elem.depth - max_depth):
                min_dif = abs(elem.depth - max_depth)
                last_nnb = elem
        # если подходядщая глубина найдена
        if last_nnb:
            context['delta_depth'] = max_depth
            context['delta_corner'] = round(last_nnb.corner - last_igirgi.corner, 2)
            context['delta_azimut'] = round(last_nnb.azimut - last_igirgi.azimut, 2)
            context['depths'] = {'nnb': last_nnb.depth, 'igirgi': max_depth}
    return context