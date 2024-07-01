import math
from math import sqrt, atan2, degrees

from django.db import models
from django import forms
from Field.models import Run


# class Request(models.Model):
#     file = models.FileField('файл')


class List(models.Model):
    """Модель с заголовками [какая-то старая модель Егора, нужно разобраться]"""
    depth = models.TextField('Глубина', max_length=200)
    CX = models.TextField('GX', max_length=200)
    CY = models.TextField('GY', max_length=200)
    CZ = models.TextField('GZ', max_length=200)
    BX = models.TextField('BX', max_length=200)
    BY = models.TextField('BY', max_length=200)
    BZ = models.TextField('BZ', max_length=200)

    class Meta:
        verbose_name = 'Лист заголовков'
        verbose_name_plural = 'Листы заголовков'


class Device(models.Model):
    """Модель под телесистему [Коэффициенты пересчета]"""
    device_title = models.CharField('Название телесистемы', max_length=100, unique=True)
    CX = models.CharField('GX', max_length=50)
    CY = models.CharField('GY', max_length=50)
    CZ = models.CharField('GZ', max_length=50)
    BX = models.CharField('BX', max_length=50)
    BY = models.CharField('BY', max_length=50)
    BZ = models.CharField('BZ', max_length=50)

    def __str__(self):
        return self.device_title

    class Meta:
        verbose_name = 'Телесистема'
        verbose_name_plural = 'Телесистемы'


class Data(models.Model):
    """Один из замеров под рейс"""
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    depth = models.FloatField('Глубина', max_length=10)
    CX = models.FloatField('GX', max_length=10, null=True)
    CY = models.FloatField('GY', max_length=10, null=True)
    CZ = models.FloatField('GZ', max_length=10, null=True)
    BX = models.FloatField('BX', max_length=10, null=True)
    BY = models.FloatField('BY', max_length=10, null=True)
    BZ = models.FloatField('BZ', max_length=10, null=True)
    Btotal_corr = models.FloatField('Btotal_corr', null=True)
    DIP_corr = models.FloatField('DIP_corr', null=True)
    in_statistics = models.BooleanField('Учитывать в статистике', null=True)
    comment = models.TextField('Комментарий', default='', null=True, blank='True')

    def __str__(self):
        return str(self.run) + ' ' + str(self.depth)

    class Meta:
        verbose_name = 'Данные'
        verbose_name_plural = 'Данные'

    # def comment_template(self):
    #     """Вывод комментария на страницу (чтобы не отображать None в поле)"""
    #     return self.comment if self.comment is not None else ''

    def Btotal_corrFix(self):
        """Округленное значение"""
        return round(self.Btotal_corr, 4) if self.Btotal_corr is not None else '-'

    def DIP_corrFix(self):
        """Округленное значение"""
        return round(self.DIP_corr, 2) if self.DIP_corr is not None else '-'

    def Gtotal(self):
        return round(sqrt(self.CX ** 2 + self.CY ** 2 + self.CZ ** 2), 5)

    def Btotal(self):
        return round(sqrt(self.BX ** 2 + self.BY ** 2 + self.BZ ** 2), 1)

    def Dip(self):
        try:
            dip = abs(round(math.degrees(math.asin(
                (self.CX * self.BX + self.CY * self.BY + self.CZ * self.BZ) /
                (sqrt(self.CX ** 2 + self.CY ** 2 + self.CZ ** 2) * sqrt(self.BX ** 2 + self.BY ** 2 + self.BZ ** 2)))),
                2))
        except:
            dip = None
        return dip

    def Zenit(self):
        return round(math.degrees(math.acos(self.CZ / sqrt(self.CX ** 2 + self.CY ** 2 + self.CZ ** 2))), 2)

    def Azimut(self):
        azim = round(math.degrees(math.atan2(
            (self.CX * self.BY - self.CY * self.BX) * self.Gtotal(),
            self.BZ * (self.CX ** 2 + self.CY ** 2) - self.CZ * (self.CX * self.BX + self.CY * self.BY), )), 2)
        return azim if azim > 0 else round(azim + 360, 2)

    def ItogAzimut(self):
        """Азимут с поправками картографический или географический"""
        azim = round(math.degrees(math.atan2(
            (self.CX * self.BY - self.CY * self.BX) * self.Gtotal(),
            self.BZ * (self.CX ** 2 + self.CY ** 2) - self.CZ * (self.CX * self.BX + self.CY * self.BY),))
                     + (self.run.section.wellbore.well_name.total_correction if
                        self.run.section.wellbore.well_name.total_correction is not None else 0), 2)
        return azim if azim > 0 else round(azim + 360, 2)

    # Отображение на страницу в input type="number" не поддерживает .
    def depth_dot(self) -> str:
        return str(self.depth).replace(",", ".")

    def CX_dot(self) -> str:
        return str(self.CX).replace(",", ".")

    def CY_dot(self) -> str:
        return str(self.CY).replace(",", ".")

    def CZ_dot(self) -> str:
        return str(self.CZ).replace(",", ".")

    def BX_dot(self) -> str:
        return str(self.BX).replace(",", ".")

    def BY_dot(self) -> str:
        return str(self.BY).replace(",", ".")

    def BZ_dot(self) -> str:
        return str(self.BZ).replace(",", ".")

    def Btotal_corr_dot(self) -> float:
        return str(self.Btotal_corr).replace(",", ".")

    def DIP_corr_dot(self) -> float:
        return str(self.DIP_corr).replace(",", ".")

    def get_goxy(self) -> float:
        return sqrt(self.CX ** 2 + self.CY ** 2)

    def get_boxy(self) -> float:
        return sqrt(self.BX ** 2 + self.BY ** 2)

    def get_hstf(self) -> int:
        hstf = (degrees(atan2(-self.CX, -self.CY)) - 90) % 360
        return int(hstf)


class AxesFileIndex(models.Model):
    """Индексы под загружаемые файлы осей"""
    GX = models.CharField('GX', max_length=4)
    GY = models.CharField('GY', max_length=4)
    GZ = models.CharField('GZ', max_length=4)
    BX = models.CharField('BX', max_length=4)
    BY = models.CharField('BY', max_length=4)
    BZ = models.CharField('BZ', max_length=4)
    units = models.CharField('Строка единиц измерения', max_length=4)
    string_index = models.CharField('Импорт со строки', max_length=4)
    depth = models.CharField('Глубина', max_length=4)
    run = models.OneToOneField(Run, on_delete=models.CASCADE, null=True)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = 'Индесы телесистемы'
        verbose_name_plural = 'Индесы телесистемы'
