from django.db import models
from Field.models import Run, Wellbore


class Meas(models.Model):
    """ Абстрактный класс замера """
    depth = models.FloatField('глубина')
    corner = models.FloatField('угол', null=True)
    azimut = models.FloatField('азимут', null=True)
    run = models.ForeignKey(Run, on_delete=models.CASCADE, null=True)

    class Meta:
        abstract = True
        ordering = ['depth']


class GraphParam(models.Model):
    """ Абстрактный класс для параметров масштаба графиков контроля качества """
    x_min = models.FloatField('Минимальное значение по X')
    x_max = models.FloatField('Максимальное значение по X')
    x_del = models.FloatField('Шаг по X', null=True)
    y_min = models.FloatField('Минимальное значение по Y')
    y_max = models.FloatField('Максимальное значение по Y')
    y_del = models.FloatField('Шаг по Y', null=True)
    wellbore = models.OneToOneField(Wellbore, on_delete=models.CASCADE)

    def get_title(self):
        return 'График контроля качества'

    class Meta:
        abstract = True


class Graf1Param(GraphParam):
    class Meta:
        db_table = 'report_graph1'


class Graf2Param(GraphParam):
    class Meta:
        db_table = 'report_graph2'


class Graf3Param(GraphParam):
    class Meta:
        db_table = 'report_graph3'


class Graf4Param(GraphParam):
    class Meta:
        db_table = 'report_graph4'


class Graf5Param(GraphParam):
    class Meta:
        db_table = 'report_graph5'


class Graf6Param(GraphParam):
    class Meta:
        db_table = 'report_graph6'


class ProjectionParam(models.Model):
    """Параметры для постройки графиков проекции [Отчёт]"""
    hor_x_min = models.IntegerField('Минимальное значение по X (Запад/Восток)', null=True)
    hor_x_max = models.IntegerField('Максимальное значение по X (Запад/Восток)', null=True)
    hor_x_del = models.IntegerField('Шаг по X (Запад/Восток)', null=True)
    hor_y_min = models.IntegerField('Минимальное значение по Y (Юг/Север)', null=True)
    hor_y_max = models.IntegerField('Максимальное значение по Y (Юг/Север)', null=True)
    hor_y_del = models.IntegerField('Шаг по Y (Юг/Север)', null=True)
    ver_x_min = models.IntegerField('Минимальное значение по X (Вертикальная секция)', null=True)
    ver_x_max = models.IntegerField('Максимальное значение по X (Вертикальная секция)', null=True)
    ver_x_del = models.IntegerField('Шаг по X (Вертикальная секция)', null=True)
    ver_y_min = models.IntegerField('Минимальное значение по Y (Абсолютная отметка)', null=True)
    ver_y_max = models.IntegerField('Максимальное значение по Y (Абсолютная отметка)', null=True)
    ver_y_del = models.IntegerField('Шаг по Y (Абсолютная отметка)', null=True)

    wellbore = models.ForeignKey(Wellbore,
                                 on_delete=models.CASCADE,
                                 verbose_name='Параметры проекции',
                                 related_name='proj_params',
                                 )

    class Meta:
        verbose_name = 'Параметры для построения проекции'
        verbose_name_plural = 'Параметры для построения проекции'
        db_table = 'report_proj_graph'


class ReportIndex(models.Model):
    """ Модель для запоминания полей в report форме [для импорта файлов с замерами]"""
    raw_dynamic_depth = models.CharField("Сырые динамические глубина", max_length=10, null=True)
    raw_dynamic_corner = models.CharField("Сырые динамические угол", max_length=10, null=True)
    raw_dynamic_depth_excel = models.CharField("Сырые динамические глубина excel", max_length=10, null=True)
    raw_dynamic_corner_excel = models.CharField("Сырые динамические угол excel", max_length=10, null=True)
    raw_dynamic_list_name = models.CharField("Сырые динамические лист эксель", max_length=10, null=True)

    nnb_static_depth = models.CharField("Статические от ННБ глубина", max_length=10, null=True)
    nnb_static_corner = models.CharField("Статические от ННБ угол", max_length=10, null=True)
    nnb_static_azimut = models.CharField("Статические от ННБ азимут", max_length=10, null=True)
    nnb_static_list_name = models.CharField("Статические от ННБ лист эксель", max_length=10, null=True)
    nnb_static_exclude_proj = models.BooleanField("Флаг на исключение проекции", default=False)

    nnb_dynamic_depth = models.CharField("Динамические от ННБ глубина", max_length=10, null=True)
    nnb_dynamic_corner = models.CharField("Динамические от ННБ угол", max_length=10, null=True)
    nnb_dynamic_azimut = models.CharField("Динамические от ННБ азимут", max_length=10, null=True)
    nnb_dynamic_list_name = models.CharField("Динамические от ННБ лист эксель", max_length=10, null=True)

    igirgi_static_depth = models.CharField("Статические ИГиРГИ глубина", max_length=10, null=True)
    igirgi_static_corner = models.CharField("Статические ИГиРГИ угол", max_length=10, null=True)
    igirgi_static_azimut = models.CharField("Статические ИГиРГИ азимут", max_length=10, null=True)
    igirgi_list_name = models.CharField("Статические ИГиРГИ лист эксель", max_length=10, null=True)

    plan_depth = models.CharField("Плановая траектория глубина", max_length=10, null=True)
    plan_corner = models.CharField("Плановая траектория угол", max_length=10, null=True)
    plan_azimut = models.CharField("Плановая траектория азимут", max_length=10, null=True)
    plan_list_name = models.CharField("Плановая траектория лист эксель", max_length=10, null=True)

    nnb_dynamic_read = models.IntegerField("Считываем динамические данные  от ННБ с этой строки", null=True)
    nnb_static_read = models.IntegerField("Считываем статические данные от ННБ с этой строки", null=True)
    plan_str = models.IntegerField("Считываем данные плана с этой строки", null=True)
    igirgi_str = models.IntegerField("Считываем данные статика ИГиРГИ с этой строки", null=True)
    raw_str = models.IntegerField("Считываем сырые данные с этой строки", null=True)

    run = models.OneToOneField(Run, on_delete=models.CASCADE, unique=True)

    class Meta:
        verbose_name = 'Индекс для формы'
        verbose_name_plural = 'Индексы для формы'
        db_table = 'report_trajectory_index'


class DynamicNNBData(Meas):
    """Динамические замеры ННБ"""

    def __str__(self):
        return f"Глубина {self.depth}"

    class Meta:
        ordering = ['depth']
        verbose_name = 'Динамический замер ННБ'
        verbose_name_plural = 'Динамические замеры ННБ'
        db_table = 'meas_dynamic_NNB'


class StaticNNBData(Meas):
    """Статические замеры ННБ"""

    def __str__(self):
        return f"Глубина {self.depth}"

    class Meta:
        ordering = ['depth']
        verbose_name = 'Статический замер ННБ'
        verbose_name_plural = 'Статические замеры ННБ'
        db_table = 'meas_static_NNB'


class IgirgiStatic(Meas):
    """Статические замеры ИГИРГИ"""
    comment = models.TextField('комментарий', null=True)

    def __str__(self):
        return f"Глубина {self.depth}"

    class Meta:
        ordering = ['depth']
        verbose_name = 'Статический замер ИГИРГИ'
        verbose_name_plural = 'Статические замеры ИГИРГИ'
        db_table = 'meas_static_igirgi'


class IgirgiDynamic(Meas):
    """Динамические замеры ИГИРГИ"""

    def __str__(self):
        return f"Глубина {self.depth}"

    class Meta:
        ordering = ['depth']
        verbose_name = 'Динамический замер ИГИРГИ'
        verbose_name_plural = 'Динамические замеры ИГИРГИ'
        db_table = 'meas_dynamic_igirgi'


class Raw(Meas):
    """Сырые данные полученные до обработки"""

    def __str__(self):
        return f"Глубина {self.depth}"

    class Meta:
        ordering = ['depth']
        verbose_name = 'Сырой замер'
        verbose_name_plural = 'Сырые замер'
        db_table = 'meas_raw'


class Plan(Meas):
    """Плановые замеры ННБ"""
    plan_version = models.CharField('версия плана', max_length=20, null=True)

    def __str__(self):
        return f"Глубина {self.depth}"

    class Meta:
        ordering = ['depth']
        verbose_name = 'Замер плановой траектории'
        verbose_name_plural = 'Замеры плановой траектории'
        db_table = 'meas_plan'


class InterpPlan(Meas):
    """
    План интерполированный по глубине замеров ИГиРГИ для бурения по траектории ИГиРГИ [замена траектории ННБ]
    """

    class Meta:
        ordering = ['depth']
        verbose_name = 'Замер интерполированной плановой траектории'
        verbose_name_plural = 'Замеры интерполированной плановой траектории'
        db_table = 'meas_intr_plan'


def get_run_by_id(run_id):
    """Нужно будет убрать"""
    return Run.objects.get(id=run_id)
