from rest_framework import serializers

from .models import *


class DataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Data
        fields = '__all__'


class FileSerializer(serializers.ModelSerializer):
    """ Телесистема с индексами для чтения файла осей"""
    class Meta:
        model = AxesFileIndex
        fields = '__all__'


class DeviceSerializer(serializers.ModelSerializer):
    """ Телесистема с коэф пересчёта """
    class Meta:
        model = Device
        fields = '__all__'