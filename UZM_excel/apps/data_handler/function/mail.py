from report.function.model_service import last_depth, waste


class BodyData:
    """ Даннные под тело письма get_body - формирует текст письма"""

    def __init__(self, Wellbore: object):
        """Создание тела письма"""
        self.field = Wellbore.well_name.pad_name.field.field_name
        self.pad = Wellbore.well_name.pad_name.pad_name
        self.well = Wellbore.well_name.well_name
        self.depth = last_depth(Wellbore)
        self.departure = ''  # Берём отходы в fetch запросе с сервера функция report из report/views
        self.horiz = ''  # Горизантальные отходы
        self.vert = ''  # вертикальные отходы


class Letter:
    """ Здесь хранятся данные для пиьсма """

    def __init__(self, Wellbore: object, plan_version):
        """ Передаем экземпляр скважины по которой отправляем отчёт """
        self.data_body = BodyData(Wellbore)
        self.subject = 'test'  # тема письма будет заполняться в js функции при выдаче файла (нужны отходы с отчета)
        self.mailto = (Wellbore.well_name.mail_To.replace('\r\n',
                                                          ' ') if Wellbore.well_name.mail_To != '' else 'None')  # кому отправить
        self.cc = (
            Wellbore.well_name.mail_Cc.replace('\r\n', ' ') if Wellbore.well_name.mail_Cc != '' else 'None')  # копия
        # тело письма
        self.warning = 'Бурение ведётся по траектории ИГиРГИ%0D%0A' if Wellbore.igirgi_drilling else ''
        #if plan_version!='-':
            #self.text_part = 'от плановой траектории '+ plan_version if Wellbore.igirgi_drilling else 'от траектории подрядчика ННБ'
        #else:
            #self.text_part = 'от плановой траектории' if Wellbore.igirgi_drilling else 'от траектории подрядчика ННБ'
        self.text_part='от траектории подрядчика ННБ'
        self.body = 'Это тело письма'  # get_body() - перезаписывает все переменные ниже
        self.comm_waste = "Это строка с общими отходами"
        self.hor_waste = 'Это строка с горизонтальными отходами'
        self.ver_waste = 'Это строка с вертикальными отходами'
        self.endbody = 'Это конец письма'
        self.get_body()

    def get_body(self):
        """Из записанных параметров скважины формируем string"""
        # %0D%0A - enter
        self.body = f"Контроль качества инклинометрии во время бурения:%0D%0A %0D%0A" \
                    f"Месторождение: {self.data_body.field}%0D%0A" \
                    f"Куст: {self.data_body.pad}%0D%0A" \
                    f"Скважина: {self.data_body.well}%0D%0A" \
                    f"{self.warning}"\
                    f"%0D%0AОбщий отход на точку замера {self.data_body.depth} м {self.text_part} составляет "
        self.comm_waste = f" {self.data_body.departure} м;%0D%0A %0D%0A"
        self.hor_waste = f"По горизонтали : {self.data_body.horiz}"
        self.ver_waste = f"; %0D%0A %0D%0AПо вертикали : {self.data_body.vert}"
        self.endbody = f".%0D%0A"
