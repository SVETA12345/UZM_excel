from django import template

register = template.Library()


@register.filter(name='comment')
def nnb_comment_by_Index(indexable, i) -> str:
    """забираем комментарий у замера (в indexable только NNB_static_meas)"""
    if indexable[i].comment is not None:
        return indexable[i].comment
    else:
        return ''
