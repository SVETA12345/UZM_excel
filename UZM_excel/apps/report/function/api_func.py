"""Здесь прописаны функции для api функций под fetch запросы,
 возращает json вместо шаблонов"""
from django.http import JsonResponse
from ..models import ReportIndex
from Field.models import Run


def get_index(request) -> JsonResponse:
    """Возвращает индексы для считывания файла по выбранному рейсу"""
    run_id = request.POST.get('run_id')
    if run_id != "Выберите рейс":
        obj = Run.objects.get(id=run_id)
        try:
            report_index = ReportIndex.objects.get(run=obj)
            return JsonResponse({
                'raw_depth': report_index.raw_dynamic_depth,
                'raw_corner': report_index.raw_dynamic_corner,
                'raw_list_name': report_index.raw_dynamic_list_name,
                'nnb_static_depth': report_index.nnb_static_depth,
                'nnb_static_corner': report_index.nnb_static_corner,
                'nnb_static_azimut': report_index.nnb_static_azimut,
                'nnb_static_list_name': report_index.nnb_static_list_name,
                'nnb_dynamic_depth': report_index.nnb_dynamic_depth,
                'nnb_dynamic_corner': report_index.nnb_dynamic_corner,
                'nnb_dynamic_azimut': report_index.nnb_dynamic_azimut,
                'nnb_dynamic_list_name': report_index.nnb_dynamic_list_name,
                'nnb_static_exclude_proj': report_index.nnb_static_exclude_proj,
                'igirgi_static_depth': report_index.igirgi_static_depth,
                'igirgi_static_corner': report_index.igirgi_static_corner,
                'igirgi_static_azimut': report_index.igirgi_static_azimut,
                'igirgi_static_list_name': report_index.igirgi_list_name,
                'igirgi_str': report_index.igirgi_str,
                'plan_depth': report_index.plan_depth,
                'plan_corner': report_index.plan_corner,
                'plan_azimut': report_index.plan_azimut,
                'plan_list_name': report_index.plan_list_name,
                "plan_str": report_index.plan_str,
                'nnb_dynamic_read': report_index.nnb_dynamic_read,  # read номер строки с которой начинаем считывание
                'nnb_static_read': report_index.nnb_static_read, })
        except:
            pass

    return full_none


full_none = JsonResponse({
    'raw_depth': '',
    'raw_corner': '',
    'raw_list_name': '',
    'nnb_static_depth': '',
    'nnb_static_corner': '',
    'nnb_static_azimut': '',
    'nnb_static_list_name': '',
    'nnb_dynamic_depth': '',
    'nnb_dynamic_corner': '',
    'nnb_dynamic_azimut': '',
    'nnb_dynamic_list_name': '',
    'igirgi_static_depth': '',
    'igirgi_static_corner': '',
    'igirgi_static_azimut': '',
    'igirgi_static_list_name': '',
    'plan_depth': '',
    'plan_corner': '',
    'plan_azimut': '',
    'plan_list_name': '',
    "plan_str": '',
    'nnb_dynamic_read': '',
    'nnb_static_read': '',
    'igirgi_str': '', })
