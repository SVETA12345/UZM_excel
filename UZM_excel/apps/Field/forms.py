import re

from django.forms import ModelForm, widgets

from . import models


class AddContractorNNBForm(ModelForm):
    class Meta:
        model = models.ContractorNNB
        fields = '__all__'


class AddContractorDrillForm(ModelForm):
    class Meta:
        model = models.ContractorDrill
        fields = '__all__'


class AddFieldForm(ModelForm):
    class Meta:
        model = models.Field
        fields = '__all__'


class AddPadForm(ModelForm):
    class Meta:
        model = models.Pad
        fields = '__all__'


class AddWellForm(ModelForm):
    """Форма для ручного добавления модели скважины"""
    class Meta:
        model = models.Well
        fields = '__all__'
        widgets = {
            'geomagnetic_date': widgets.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'T1_start': widgets.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'T1_end': widgets.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'T3_start': widgets.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'T3_end': widgets.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'latitude': widgets.TextInput(),
            'longtitude': widgets.TextInput(),
        }

    def mail_replace(self) -> None:
        """Облегчает вставку почты из Outlook"""
        _mutable = self.data._mutable
        self.data._mutable = True
        if '<' in self.data['mail_To']:
            self.data['mail_To'] = ''.join(str(s)+"; " for s in re.findall('<(\S*)>', self.data['mail_To']))
        if '<' in self.data['mail_Cc']:
            self.data['mail_Cc'] = ''.join(str(s) + "; " for s in re.findall('<(\S*)>', self.data['mail_Cc']))
        self.data._mutable = _mutable

    def transform(self):
        """ [Доп. функционал] [Не используется] Преобразуем значения долготы и широты в десятичные значения """
        if self.data['latitude'] != '' or self.data['longtitude'] != '':  # Ввод КООРДИНАТЫ УСТЬЯ XX YY ZZ
            _mutable = self.data._mutable  # изменяем QueryDicts
            self.data._mutable = True
            try:
                lat_v = [float(idx) for idx in self.data['latitude'].replace(',', '.').split(' ')]
                self.data['latitude'] = (round(float(lat_v[0]) + float(lat_v[1]) / 60 + float(lat_v[2]) / 3600, 3)
                                         if len(lat_v) > 2 else float(lat_v[0]))
            except:
                self.data['latitude'] = ''

            try:
                long_v = [float(idx) for idx in self.data['longtitude'].replace(',', '.').split(' ')]
                self.data['longtitude'] = (round(float(long_v[0]) + float(long_v[1]) / 60 + float(long_v[2]) / 3600, 3)
                                           if len(long_v) > 2 else float(long_v[0]))
            except:
                self.data['longtitude'] = ''

            self.data._mutable = _mutable


class AddWellboreForm(ModelForm):
    class Meta:
        model = models.Wellbore
        exclude = ('igirgi_drilling',)
        # exclude = ['wellbore']


class AddSectionForm(ModelForm):
    class Meta:
        model = models.Section
        fields = '__all__'


class AddRunForm(ModelForm):
    """ Форма для создания экземпляра рейса"""
    class Meta:
        model = models.Run
        exclude = ['start_date', 'end_date', 'start_depth', 'end_depth']
        widgets = {
            'start_date': widgets.DateInput(attrs={'type': 'date'}),
            'end_date': widgets.DateInput(attrs={'type': 'date'}),
        }


class EditRunForm(ModelForm):
    """ Форма для редактирования параметров рейса"""
    class Meta:
        model = models.Run
        fields = '__all__'
        widgets = {
            'start_date': widgets.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'end_date': widgets.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }


class AddClientForm(ModelForm):
    class Meta:
        model = models.Client
        fields = '__all__'
