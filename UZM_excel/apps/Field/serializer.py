from rest_framework import serializers
from .models import *


# class ClientSerializer(serializers.Serializer):
#     client_name = serializers.CharField()
#
#     def create(self, validated_data):
#         return Client.objects.create(**validated_data)

class ClientSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField()

    class Meta:
        model = Client
        fields = '__all__'
        read_only_fields = ('full_name',)


class ContractorNNBSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractorNNB
        fields = '__all__'


class ContractorDrillSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractorDrill
        fields = '__all__'


class WellSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='get_client', read_only=True)
    contractorNNB = serializers.CharField(source='get_contractor', read_only=True)
    field_name = serializers.CharField(source='get_field_name', read_only=True)

    class Meta:
        model = Well
        fields = '__all__'
        extra_kwargs = {
            'pad_id': {'source': 'pad_name'},
        }


class ContractorNNBSerializer_Add(serializers.ModelSerializer):
    """Сериализатор для подрядчика ДЛЯ СОЗДАНИЯ МОДЕЛЕЙ """

    class Meta:
        model = ContractorNNB
        fields = ['Подрядчики по ННБ', ]
        extra_kwargs = {
            'Подрядчики по ННБ': {'source': 'dd_contractor_name', 'read_only': True},
        }
        order_by = ('Подрядчики по ННБ',)


class ContractorDrillSerializer_Add(serializers.ModelSerializer):
    """Сериализатор для подрядчика ДЛЯ СОЗДАНИЯ МОДЕЛЕЙ """

    class Meta:
        model = ContractorDrill
        fields = ['Подрядчики по бурению', ]
        extra_kwargs = {
            'Подрядчики по бурению': {'source': 'drill_contractor_name', 'read_only': True},
        }
        order_by = ('Подрядчики по бурению',)


class PadnameSerializer(serializers.ModelSerializer):
    """Сериализатор для куста с именами (имя) ДЛЯ СОЗДАНИЯ МОДЕЛЕЙ """

    # field_name = serializers.CharField(source='get_field', read_only=True)

    class Meta:
        model = Pad
        fields = ['Месторождение', 'Куст']
        extra_kwargs = {
            'Месторождение': {'source': 'get_field', 'read_only': True},
            'Куст': {'source': 'pad_name', 'read_only': True},
        }
        order_by = ('Месторождение',)


class FieldnameSerializer(serializers.ModelSerializer):
    """Сериализатор для месторождения с именами (имя) ДЛЯ СОЗДАНИЯ МОДЕЛЕЙ """

    # client_name = serializers.CharField(source='get_client', read_only=True)

    class Meta:
        model = Field
        fields = ['ДО', 'Месторождение', ]
        extra_kwargs = {
            'ДО': {'source': 'get_client', 'read_only': True},
            'Месторождение': {'source': 'field_name', 'read_only': True},
        }


class PadSerializer(serializers.ModelSerializer):
    """Сериализатор для Куста с Скважиной"""
    wells = WellSerializer(many=True)

    class Meta:
        model = Pad
        fields = ['id', 'field', 'pad_name', 'wells']
        read_only_fields = ('wells',)
        extra_kwargs = {
            'field_id': {'source': 'field', 'write_only': True},
        }


class FieldSerializer(serializers.ModelSerializer):
    """Сериализатор для месторождения"""

    # pads = PadSerializer(many=True)

    class Meta:
        model = Field
        fields = ['id', 'field_name']


class RunSerializer(serializers.ModelSerializer):
    section_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Run
        fields = '__all__'
        extra_kwargs = {
            'section_id': {'source': 'section', 'read_only': True},
        }

    def get_section_name(self, obj):
        """Для section name"""
        try:
            obj.section
            return str(obj.section.section)
        except:
            return 'None'


class SectionSerializer(serializers.ModelSerializer):
    runs = RunSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = '__all__'


class WellboreSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True, read_only=True)
    wellbore_name = serializers.CharField(source='get_full_wellbore_name', read_only=True)

    class Meta:
        model = Wellbore
        fields = ('wellbore_name', 'wellbore', 'well_name', 'sections', 'igirgi_drilling', 'current_depth')
        read_only_fields = ('wellbore_name',)
        extra_kwargs = {
            'wellbore': {'write_only': True},
        }


class WellWithRunSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)  # по умолчанию берем данные из метода get_
    wellbores = WellboreSerializer(many=True, read_only=True)

    # sections = SectionSerializer(many=True, read_only=True)
    # runs = RunSerializer(many=True, read_only=True)

    class Meta:
        model = Well
        depth = 1
        fields = ('id', 'well_name', 'full_name', 'wellbores')

    def get_full_name(self, obj):
        return str(obj)
