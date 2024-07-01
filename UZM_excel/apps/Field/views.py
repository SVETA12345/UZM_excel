from django.http import JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from . import serializer
from .forms import *
from .models import *
from .serializer import ContractorNNBSerializer_Add, ContractorDrillSerializer_Add


def add_contractor_nnb(request):
    form = AddContractorNNBForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
        return redirect(add_contractor_drill)

    context = {"title": 'Подрядчик',
               "form": form,
               "method": "add_contractor_nnb",
               "data": sorted(ContractorNNBSerializer_Add(ContractorNNB.objects.all(), many=True).data,
                              key=lambda x: x['Подрядчики по ННБ'])}
    return render(request, 'Field/addModal.html', {'context': context, })


def add_contractor_drill(request):
    form = AddContractorDrillForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
        return redirect(add_field)

    context = {"title": 'Подрядчик',
               "form": form,
               "method": "add_contractor_drill",
               "data": sorted(ContractorDrillSerializer_Add(ContractorDrill.objects.all(), many=True).data,
                              key=lambda x: x['Подрядчики по бурению'])}
    return render(request, 'Field/addModal.html', {'context': context, })


def add_field(request):
    form = AddFieldForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
        return redirect(add_pad)

    context = {"title": 'Месторождение',
               "form": form,
               "method": "add_field",
               "data": sorted(serializer.FieldnameSerializer(Field.objects.all(), many=True).data, key=lambda x: x['ДО'])}
    return render(request, 'Field/addModal.html', {'context': context, })


def add_pad(request):
    form = AddPadForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
        return redirect(add_well)

    context = {"title": 'Куст',
               "form": form,
               "method": "add_pad",
               "data": sorted(serializer.PadnameSerializer(Pad.objects.all(), many=True).data, key=lambda x: x['Месторождение'])}
    return render(request, 'Field/addModal.html', {'context': context, })


def add_well(request):
    form = AddWellForm(request.POST)
    form.base_fields['mail_To'].help_text = 'Введите адреса через ";"'
    form.base_fields['mail_Cc'].help_text = 'Введите адреса через ";"'
    if request.method == 'POST':
        form.mail_replace()
        if form.is_valid():
            form.save()
        return redirect(add_wellbore)

    context = {"title": 'Скважина',
               "form": form,
               "method": "add_well",
               "search": Pad.objects.all()}

    return render(request, 'Field/addWell.html', {'context': context, })


def add_wellbore(request):
    form = AddWellboreForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect(add_section)
        else:
            print(form.errors.as_data())  # here you print errors to terminal

    context = {"title": 'Ствол',
               "form": form,
               "method": "add_wellbore",
               "search": Well.objects.all()}
    return render(request, 'Field/addWellbore.html', {'context': context, })


def add_section(request):
    form = AddSectionForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect(add_run)
        else:
            print(form.errors.as_data())  # here you print errors to terminal

    context = {"title": 'Секция',
               "form": form,
               "method": "add_section",
               "search": Wellbore.objects.all()}
    return render(request, 'Field/addSection.html', {'context': context, })


def add_run(request):
    form = AddRunForm(request.POST)
    form.base_fields['run_number'].help_text = 'Чтобы задать материнский ствол в поле "Рейс" укажите "-1".'
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('index_page')
        else:
            print(form.errors.as_data())  # here you print errors to terminal

    context = {"title": 'Рейс',
               "form": form,
               "method": "add_run",
               "search": Section.objects.all()}
    return render(request, 'Field/addRun.html', {'context': context, })


def clone_wellbore(request):
    """ Клонирует все модели стоящие ниже переданного ствола """
    # print(request.POST)
    old_wellbore = Wellbore.objects.get(id=request.POST['wellbore_id'])
    new_wellbore = Wellbore.objects.create(well_name=old_wellbore.well_name, wellbore=request.POST['wellbore_name'])
    for old_section in Section.objects.filter(wellbore=old_wellbore):
        new_section = Section.objects.create(section=old_section.section, wellbore=new_wellbore,
                                             target_depth=old_section.target_depth)
        for old_run in Run.objects.filter(section=old_section):
            new_run = Run.objects.create(run_number=old_run.run_number, section=new_section,
                                         start_date=old_run.start_date,
                                         end_date=old_run.end_date,
                                         start_depth=old_run.start_depth,
                                         end_depth=old_run.end_depth,
                                         in_statistics=old_run.in_statistics,
                                         memory=old_run.memory,
                                         bha=old_run.bha,
                                         sag=old_run.sag,
                                         dd_contractor_name=old_run.dd_contractor_name)

    return JsonResponse({'old_wellbore': old_wellbore.id, 'new_wellbore': new_wellbore.id})


def well_summary(request):
    """Добавляем новый комментарий в сводку"""
    if request.method == 'POST':
        WellSummary.objects.create(well=Well.objects.get(id=int(request.POST['well_id'])), text=request.POST['text'])
    if request.method == 'DELETE':
        WellSummary.objects.get(id=request.GET['id']).delete()
        return JsonResponse({'status': 'ok'})
    return redirect('param')


def edit_igirgi_drilling(request):
    """Функция переключает флаг по генерации отчётов на основе траектории ИГиРГИ"""
    obj = Wellbore.objects.get(id=request.POST['wellbore_id'])
    # obj.igirgi_drilling = (True if request.POST['status'] == 'True' else False)
    obj.igirgi_drilling = True if request.POST["status"] == 'true' else False
    obj.save()
    # print(f'Сменили режим отчёта на {request.POST["status"]}')
    return JsonResponse({'status': 'ok'})
