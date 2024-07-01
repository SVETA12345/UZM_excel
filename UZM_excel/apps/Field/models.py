import abc
from datetime import datetime

from django.core import validators
from django.db import models
from django.db.models import QuerySet
from . import choices
from .choices import get_full_choices


class Client(models.Model):
    """Дочернее общество"""
    client_name = models.CharField(
        'Заказчик',
        max_length=4,
        choices=choices.CLIENT_CHOICES,
        unique=True
    )

    class Meta:
        verbose_name = 'Дочернее общество'
        verbose_name_plural = 'Дочерние общества'

    def __str__(self):
        return get_full_choices(self.client_name, choices.CLIENT_CHOICES)


class ContractorNNB(models.Model):
    """Подрядчики по ННБ"""
    dd_contractor_name = models.CharField(
        'Подрядчик по ННБ',
        max_length=100,
        unique=True
    )

    class Meta:
        verbose_name = 'Подрядчик по ННБ'
        verbose_name_plural = 'Подрядчики по ННБ'

    def __str__(self):
        return f'{self.dd_contractor_name} '


class ContractorDrill(models.Model):
    """Подрядчики по бурению месторождения"""
    drill_contractor_name = models.CharField(
        'Подрядчик по бурению',
        max_length=100,
        unique=True
    )

    class Meta:
        verbose_name = 'Подрядчик по бурению'
        verbose_name_plural = 'Подрядчики по бурению'

    def __str__(self):
        return f'{self.drill_contractor_name}'


################################################

class Field(models.Model):
    """Месторождение"""
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        verbose_name='Заказчик',
        related_name='fields',
        null=True,
        blank=True
    )
    field_name = models.CharField('Месторождение', max_length=100, unique=True)

    class Meta:
        verbose_name = 'Месторождение'
        verbose_name_plural = 'Месторождения'

    def __str__(self):
        return self.field_name

    def get_client(self):
        """Источник в сериализаторе"""
        return str(self.client)


class Pad(models.Model):
    """Куст"""
    field = models.ForeignKey(
        Field,
        on_delete=models.CASCADE,
        verbose_name='Месторождение',
        related_name='pads',
        null=True,
        blank=True
    )
    pad_name = models.CharField('Куст', max_length=20)

    class Meta:
        verbose_name = 'Куст'
        verbose_name_plural = 'Кусты'
        unique_together = ('field', 'pad_name')

    def get_field(self):
        return str(self.field)

    def __str__(self):
        return f'{self.field}; ' \
               f'Куст.{self.pad_name}'


class Well(models.Model):
    """Скважина"""
    well_name = models.CharField('Скважина', max_length=20)
    pad_name = models.ForeignKey(
        Pad,
        on_delete=models.CASCADE,
        verbose_name='Куст',
        related_name='wells'
    )
    сontractor = models.ForeignKey(
        ContractorDrill,
        on_delete=models.SET_NULL,
        verbose_name='Подрядчик',
        related_name='wells',
        null=True,
        blank=True,
    )
    active_from = models.FloatField('Глубина начала активной фазы, м', null=True, blank=True)
    WELL_STATUS_CHOICES = [
        ('PLAN', 'Планируется'),
        ('NOTA', 'В бурении'),
        ('STOP', 'Приостановлена'),
        ('FINI', 'Добурена'),
    ]
    status = models.CharField(
        'Статус состояния скважины',
        max_length=4,
        choices=WELL_STATUS_CHOICES,
        null=True,
        blank=True
    )
    DRILL_STATUS_CHOICES = [
        ('ACTV', 'Активная фаза'),
        ('NOACT', 'Неактивная стадия'),
    ]
    status_drilling = models.CharField(
        'Статус бурения',
        max_length=5,
        choices=DRILL_STATUS_CHOICES,
        null=True,
        blank=True
    )
    in_statistics = models.BooleanField('Учитывать в статистике', null=True, blank=True)
    well_type = models.CharField(
        'Тип скважины',
        max_length=4,
        choices=choices.WELL_TYPE_CHOICES,
        null=True,
        blank=True
    )
    RKB = models.FloatField('Альтитуда стола ротора, м', null=True, blank=True, default=84)
    VSaz = models.FloatField('Азимут вертикальной секции', null=True, blank=True, default=1,
                             validators=[validators.MinValueValidator(0), validators.MaxValueValidator(360)])
    coordinate_system = models.CharField(
        'Система координат',
        max_length=20,
        null=True,
        blank=True
    )
    latitude = models.TextField('Широта географическая', null=True, blank=True)
    longtitude = models.TextField('Долгота географическая', null=True, blank=True)
    NY = models.FloatField('Широта Y (прямоугольные координаты), м', null=True, blank=True)
    EX = models.FloatField('Долгота X (прямоугольные координаты), м', null=True, blank=True)
    north_direction = models.CharField(
        'Направление на север',
        max_length=4,
        choices=choices.NORTH_DIRECTION_CHOICES,
        null=True,
        blank=True
    )
    geomagnetic_model = models.CharField('Геомагнитная модель', max_length=20, null=True, blank=True)
    geomagnetic_date = models.DateField('Дата геомагнитной привязки', null=True, blank=True)
    btotal = models.FloatField('Напряженность геомагнитного поля, нТл', null=True, blank=True)
    dip = models.FloatField('Магнитное наклонение, град', null=True, blank=True)
    dec = models.FloatField('Магнитное склонение, град', null=True, blank=True)
    grid_convergence = models.FloatField('Сближение меридианов, град', null=True, blank=True)
    total_correction = models.FloatField('Общая поправка, град', null=True, blank=True)
    gtotal = models.FloatField('Напряженность гравитационного поля, G', null=True, blank=True)
    critical_azimuth = models.BooleanField('Критический азимут', null=True, blank=True)
    T1_start = models.DateField('Начало сопровождения до Т1', null=True, blank=True)
    T1_end = models.DateField('Окончание сопровождения до Т1', null=True, blank=True)
    T3_start = models.DateField('Начало сопровождения до Т3', null=True, blank=True)
    T3_end = models.DateField('Окончание сопровождения до Т3', null=True, blank=True)
    comment = models.TextField('Комментарий', max_length=3000, null=True, blank=True)
    mail_To = models.TextField('Список рассылки почта "Кому"', max_length=3000, null=True, blank=True)
    mail_Cc = models.TextField('Список рассылки почта "Копия"', max_length=3000, null=True, blank=True)

    def get_well_type(self):
        for i in choices.WELL_TYPE_CHOICES:
            if self.well_type in i:
                return i[1]

    def get_status(self):
        for i in self.WELL_STATUS_CHOICES:
            if self.status in i:
                return i[1]

    def get_client(self):
        """Получения ДО"""
        return str(self.pad_name.field.client)

    def get_contractor(self):
        """Получение последнего подрядчика по бурению ННБ"""
        wellbores = Wellbore.objects.filter(well_name=self.id)
        if len(wellbores) != 0:
            sections = Section.objects.filter(wellbore=wellbores[0])
            if len(sections) != 0:
                runs = Run.objects.filter(section=sections[0])
                for run in runs:
                    if run.dd_contractor_name is not None and (
                            run.end_date is None or run.end_date > datetime.now().date()):
                        return run.dd_contractor_name
        return "None_contractor_name"

    def get_north_direction(self):
        """Получить полное название направления на север (Для отображения)"""
        for variant in choices.NORTH_DIRECTION_CHOICES:
            if self.north_direction in variant:
                return variant[1]

    def get_field_name(self):
        return self.pad_name.field.field_name

    def get_title(self):
        """Получаем title для выбранной скважжины"""
        return f'Куст {self.pad_name.pad_name}; Скв.{self.well_name}; {self.pad_name.field};'

    class Meta:
        verbose_name = 'Скважина'
        verbose_name_plural = 'Скважины'
        unique_together = ('well_name', 'pad_name')

    def __str__(self):
        return f'{self.pad_name}; ' \
               f'{self.well_name}'

    """Функции для шаблона с осями"""

    def btotal_graph(self):
        """Для графиков контроля (None значения не принимает)"""
        return self.btotal if self.btotal is not None else 'Null'

    def gtotal_graph(self):
        """Для графиков контроля (None значения не принимает)"""
        return self.gtotal if self.gtotal is not None else 'Null'

    def dip_graph(self):
        """Для графиков контроля (None значения не принимает)"""
        return self.dip if self.dip is not None else 'Null'

    def min_gtotal(self):
        return self.gtotal - 0.003 if self.gtotal is not None else 'Null'

    def max_gtotal(self):
        return self.gtotal + 0.003 if self.gtotal is not None else 'Null'

    def min_btotal(self):
        return self.btotal - 300 if self.btotal is not None else 'Null'

    def max_btotal(self):
        return self.btotal + 300 if self.btotal is not None else 'Null'

    def min_dip(self):
        return self.dip - 0.3 if self.dip is not None else 'Null'

    def max_dip(self):
        return self.dip + 0.3 if self.dip is not None else 'Null'


class Wellbore(models.Model):
    """Ствол"""
    well_name = models.ForeignKey(
        Well,
        on_delete=models.CASCADE,
        verbose_name='Скважина',
        related_name='wellbores',
        null=True,
        blank=True
    )
    wellbore = models.CharField(
        'Ствол',
        max_length=4,
        choices=choices.WELLBORE_CHOICES,
    )
    igirgi_drilling = models.BooleanField('Бурение по траектории ИГиРГИ', default=False, blank=True)
    current_depth = models.FloatField('Текущая глубина, м', null=True, blank=True)

    def get_contractor_name(self) -> str:
        """ Получить имя подрядчика (последнего по рейсу)"""
        runs = Run.objects.filter(section__wellbore__id=self.id).order_by('run_number').last()
        return str(runs.dd_contractor_name) if runs.dd_contractor_name is not None else '-'

    def get_choices(self):
        """Для выпадающих меню"""
        return choices.WELLBORE_CHOICES

    def get_full_wellbore_name(self):
        """Полное имя из выпадающего списка"""
        for tuple in choices.WELLBORE_CHOICES:
            if self.wellbore in tuple:
                return tuple[1]

    class Meta:
        verbose_name = 'Ствол'
        verbose_name_plural = 'Стволы'
        unique_together = ('well_name', 'wellbore')

    def __str__(self):
        return f'{self.well_name}; ' \
               f'{get_full_choices(self.wellbore, choices.WELLBORE_CHOICES)}'


class Section(models.Model):
    """Секция"""
    section = models.CharField('Секция', max_length=20)
    wellbore = models.ForeignKey(
        Wellbore,
        on_delete=models.CASCADE,
        verbose_name='Ствол',
        related_name='sections',
        null=True,
        blank=True
    )
    target_depth = models.FloatField('Плановая глубина секции, м', null=True, blank=True)

    class Meta:
        verbose_name = 'Секция'
        verbose_name_plural = 'Секции'
        unique_together = ('section', 'wellbore')

    def __str__(self):
        return f'{self.wellbore}; ' \
               f'{self.section}'


class Run(models.Model):
    """"Рейс"""
    run_number = models.IntegerField('Рейс')
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        verbose_name='Секция',
        related_name='runs',
        null=True,
        blank=True
    )
    start_date = models.DateField('Дата начала рейса', null=True, blank=True)
    end_date = models.DateField('Дата окончания рейса', null=True, blank=True)
    start_depth = models.FloatField('Глубина начала рейса', null=True, blank=True)
    end_depth = models.FloatField('Конечная глубина рейса', null=True, blank=True)
    in_statistics = models.BooleanField('Учитывать в статистике', null=True, blank=True)
    memory = models.CharField(
        'Память',
        max_length=4,
        choices=choices.MEMORY_CHOICES,
        null=True,
        blank=True
    )
    bha = models.CharField(
        'КНБК',
        max_length=4,
        choices=choices.BHA_CHOICES,
        null=True,
        blank=True
    )
    sag = models.FloatField('SAG', null=True, blank=True)
    dd_contractor_name = models.ForeignKey(
        ContractorNNB,
        on_delete=models.SET_NULL,
        verbose_name='Подрядчик по ННБ',
        related_name='runs',
        null=True,
        blank=True)

    class Meta:
        verbose_name = 'Рейс'
        verbose_name_plural = 'Рейсы'
        unique_together = ('section', 'run_number')

    def __str__(self):
        return f'{self.section}; {self.run_number};'


class WellSummary(models.Model):
    """ Сводка к скважине """
    well = models.ForeignKey(
        Well,
        on_delete=models.CASCADE,
        verbose_name='Сводка',
        related_name='summary',
        null=True,
        blank=True
    )
    text = models.TextField('Текст', null=True)
    time = models.DateTimeField('Время создания', auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name = 'Сводка'
        verbose_name_plural = 'Сводка'

    def __str__(self):
        return f'Well:{self.well} Text:{self.text};'


def get_all_run() -> QuerySet:
    """Функция взаимдействующая с Field моделью"""
    runs = Run.objects.all().order_by('-id').select_related('section__wellbore__well_name__pad_name__field__client')
    return runs


def get_all_well() -> QuerySet:
    """Получить все скважины"""
    wells = Well.objects.all()
    result = sorted(wells, key=lambda x: str(x))
    return result
