from django.forms import ModelForm

from .models import Device


class AddDeviceForm(ModelForm):
    """Добавление телесистемы"""
    class Meta:
        model = Device
        fields = '__all__'
