from rest_framework import serializers
from .models import *

# Сериализаторы под дерево


class RunNameSerializer(serializers.ModelSerializer):
    """Сериализатор для рейса"""

    class Meta:
        model = Run
        fields = ['id', 'run_number', ]


class SectionNameSerializer(serializers.ModelSerializer):
    """Сериализатор для секции"""
    runs = RunNameSerializer(many=True)

    class Meta:
        model = Section
        fields = ['id','section', 'runs', ]


class WellboreNameSerializer(serializers.ModelSerializer):
    """Сериализатор для ствола"""
    sections = SectionNameSerializer(many=True)
    wellbore = serializers.SerializerMethodField()

    class Meta:
        model = Wellbore
        fields = ['id', 'wellbore', 'sections', ]

    def get_wellbore(self, obj):
        return obj.get_full_wellbore_name()


class WellNameSerializer(serializers.ModelSerializer):
    """Сериализатор для скважины"""
    wellbores = WellboreNameSerializer(many=True)

    class Meta:
        model = Well
        fields = ['id', 'well_name', 'wellbores', ]


class PadNameSerializer(serializers.ModelSerializer):
    """Сериализатор для куста с именами"""
    wells = WellNameSerializer(many=True)

    class Meta:
        model = Pad
        fields = ['id', 'pad_name', 'wells', ]


class FieldNameSerializer(serializers.ModelSerializer):
    """Сериализатор для месторождение с именами (имя) """
    pads = PadNameSerializer(many=True)

    class Meta:
        model = Field
        fields = ['id', 'field_name', 'pads', ]


class Tree(serializers.ModelSerializer):
    fields = FieldNameSerializer(many=True)
    client = serializers.SerializerMethodField()
    class Meta:
        model = Client
        fields = ['id', 'client', 'fields', ]

    def get_client(self, obj):
        return str(obj)
