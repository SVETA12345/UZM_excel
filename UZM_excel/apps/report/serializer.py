from rest_framework import serializers

from .models import *


class ProjectionParamSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectionParam
        fields = '__all__'


class ReportIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportIndex
        fields = '__all__'
