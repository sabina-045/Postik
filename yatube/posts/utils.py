from django.core.paginator import Paginator

from . import constants
from .models import Post, Follow


def post_paginator(request, post_list):
    paginator = Paginator(post_list, constants.PAGE_POSTS_NUMBER)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return page_obj


def get_following_authors_post_list(user):
    user_authors = Follow.objects.filter(user_id=user.pk)
    authors_id_list = list(user_authors.values_list('author_id', flat=True))
    post_list = Post.objects.filter(author_id__in=authors_id_list)

    return post_list
