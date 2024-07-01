from django.shortcuts import render

from .models import Post
from Field.models import Run, Well
from .utils import get_page_obj
from report.models import IgirgiStatic


def index_page(request):
    """Функция для главной страницы"""
    # Передаем посты с пагинатором
    posts = Post.objects.all()
    page_obj = get_page_obj(posts, request)

    # Запрос на получение из базы скважин для таблицы
    wells_status_exclude = ['FINI', 'STOP']
    wells = Well.objects.exclude(
        status__in=wells_status_exclude
    ).exclude(
        status__isnull=True
    ).order_by(
        'status',
        'status_drilling',
        'pad_name__field__client'
    ).values('id')

    # Получаем последний рейс для каждой скважины + related
    runs = []
    for well in wells:
        try:
            run = (Run.objects.exclude(
                run_number='-1'
            ).select_related(
                'section__wellbore__well_name__pad_name__field__client'
            ).filter(
                section__wellbore__well_name=well['id']
            ).latest('run_number'))
            runs.append(run)
        except Run.DoesNotExist:
            pass

    # Создаем список словарей для наполнения таблицы и local storage
    runs_to_context = []
    for run in runs:

        try:
            last_survey = IgirgiStatic.objects.filter(run=run).values('depth').latest('depth')['depth']
        except IgirgiStatic.DoesNotExist:
            last_survey = 'n/a'

        try:
            if run.section.wellbore.well_name.active_from is None or isinstance(last_survey, str):
                active = 'n/a'
            elif last_survey.depth >= run.section.wellbore.well_name.active_from:
                active = 'Активная'
            else:
                active = run.section.wellbore.well_name.active_from

            runs_to_context.append(
                {
                    'client': run.section.wellbore.well_name.pad_name.field.client,
                    'field': run.section.wellbore.well_name.pad_name.field.field_name,
                    'pad': run.section.wellbore.well_name.pad_name.pad_name,
                    'well': run.section.wellbore.well_name.well_name,
                    'wellbore': run.section.wellbore.get_wellbore_display(),
                    'section': run.section.section,
                    'run_number': run.run_number,
                    'status': run.section.wellbore.well_name.get_status_display(),
                    'active': active,
                    'last_survey': last_survey,
                    # Для localstorage
                    'client_id': run.section.wellbore.well_name.pad_name.field.client.id,
                    'field_id': run.section.wellbore.well_name.pad_name.field.id,
                    'pad_id': run.section.wellbore.well_name.pad_name.id,
                    'well_id': run.section.wellbore.well_name.id,
                    'wellbore_id': run.section.wellbore.id,
                    'section_id': run.section.id,
                    'run_id': run.id
                }
            )
        except AttributeError:
            pass

    context = {
        'posts': posts,
        'page_obj': page_obj,
        'runs_to_context': runs_to_context
    }
    return render(request, 'index_page.html', context)
