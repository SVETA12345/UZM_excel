""" Функции для работы с данными моделей """
from ..models import Data
from Field.models import Wellbore, Run


def clone_wellbore_axes(request) -> str:
    """Клонирование всех замеров старого ствола в новый ствол"""
    old_wellbore = Wellbore.objects.get(id=request.POST['old_wellbore'])
    new_wellbore = Wellbore.objects.get(id=request.POST['new_wellbore'])
    data_List = []
    for old_section in old_wellbore.sections.all():
        for old_run in old_section.runs.all():
            new_run = Run.objects.get(run_number=old_run.run_number, section__wellbore=new_wellbore)

            for meas in Data.objects.filter(run=old_run):
                data_List.append(
                    Data(
                        run=new_run,
                        depth=meas.depth,
                        CX=meas.CX,
                        CY=meas.CY,
                        CZ=meas.CZ,
                        BX=meas.BX,
                        BY=meas.BY,
                        BZ=meas.BZ,
                        Btotal_corr=meas.Btotal_corr,
                        DIP_corr=meas.DIP_corr,
                        in_statistics=meas.in_statistics,
                        comment=meas.comment,
                    )
                )
    Data.objects.bulk_create(data_List)
    return 'Ok'