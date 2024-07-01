from typing import Type
from multipledispatch import dispatch

from report.models import IgirgiStatic, StaticNNBData


# from Field.models import Run, Well
#
#
# def selected_for_tree(context: dict, obj: object) -> dict:
#     """На основе выбранного рейса узнаем какие модели выбраны выше"""
#     if isinstance(obj, Run):
#         run = obj
#         context['selected_client'] = str(run.section.wellbore.well_name.pad_name.field.client)
#         context['selected_field'] = run.section.wellbore.well_name.pad_name.field.field_name
#         context['selected_pad'] = run.section.wellbore.well_name.pad_name.pad_name
#         context['selected_well'] = run.section.wellbore.well_name.well_name
#         context['selected_wellbore'] = run.section.wellbore.get_full_wellbore_name()
#         context['selected_section'] = run.section.section
#         context['selected_run'] = run.run_number
#     elif isinstance(obj, Well):
#         well = obj
#         context['selected_client'] = str(well.pad_name.field.client)
#         context['selected_field'] = well.pad_name.field.field_name
#         context['selected_pad'] = well.pad_name.pad_name
#         # context['selected_well'] = well.well_name


