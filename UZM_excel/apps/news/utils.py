from django.core.paginator import Paginator

from .consts import POSTS_NUM


def get_page_obj(posts, request):
    paginator = Paginator(posts, POSTS_NUM)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
