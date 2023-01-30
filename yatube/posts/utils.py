from django.core.paginator import Paginator

from . import constants


def post_paginator(request, post_list):
    paginator = Paginator(post_list, constants.PAGE_POSTS_NUMBER)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return page_obj
