from django.shortcuts import render


def main_index(request):
    context = {"title": 'Главная'}
    return render(request, 'base.html', {'context': context, })
