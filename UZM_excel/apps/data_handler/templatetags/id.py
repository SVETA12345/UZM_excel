from django import template

register = template.Library()


@register.filter(name='id')
def nnb_id_by_Index(indexable, i) -> int:
    """забираем id у замера (в indexable только NNB_static_meas)"""
    return indexable[i].id
