from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from posts.utils import post_paginator, get_following_authors_post_list

from .forms import CommentForm, PostForm
from .models import Group, Post, User, Follow


@cache_page(20, key_prefix='index_page')
def index(request):
    """Последние посты на сайте"""
    post_list = Post.objects.all()
    context = {
        'page_obj': post_paginator(request, post_list),
    }

    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Список постов группы"""
    group = get_object_or_404(Group, slug=slug)
    group_posts_list = group.posts.all()
    context = {
        'page_obj': post_paginator(request, group_posts_list),
        'group': group
    }

    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Запрос в профайл пользователя"""
    author = get_object_or_404(User, username=username)
    author_posts_list = Post.objects.filter(author=author)
    user = request.user
    try:
        following = Follow.objects.get(
            user_id=user.pk,
            author_id=author.pk)
    except Follow.DoesNotExist:
        following = False
    context = {
        'page_obj': post_paginator(request, author_posts_list),
        'author': author,
        'following': following
    }

    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Просмотр детальной информации отдельного поста"""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    comments = post.comment.all()
    context = {
        'post': post,
        'form': form,
        'comments': comments
    }

    return render(request, 'posts/post_detail.html', context)


@login_required
def add_comment(request, post_id):
    """Добавление комментария."""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

        return redirect('posts:post_detail', post_id=post_id)

    return redirect('posts:post_detail', {'form': form}, post_id=post_id)


@login_required
def post_create(request):
    """Создание нового поста."""
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()

        return redirect('posts:profile', username=post.author)

    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    """Редактирование поста."""
    post = get_object_or_404(Post, id=post_id)
    if request.user == post.author:
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post
        )
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            return redirect('posts:post_detail', post_id)
    else:

        return redirect('posts:post_detail', post_id)

    context = {
        'form': form,
        'post': post,
        'is_edit': True
    }

    return render(request, 'posts/create_post.html', context)


@login_required
def follow_index(request):
    """Список постов авторов, на которых подписался пользователь."""
    user = request.user
    context = {
        'page_obj': post_paginator(
            request,
            get_following_authors_post_list(user))
    }

    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Подписаться на автора поста."""
    author = get_object_or_404(User, username=username)
    user = request.user
    if not Follow.objects.filter(
            user_id=user.pk,
            author_id=author.pk).exists() and author != user:
        Follow(user_id=user.pk, author_id=author.pk).save()
    context = {
        'page_obj': post_paginator(
            request,
            get_following_authors_post_list(user))
    }

    return render(request, 'posts/follow.html', context)


@login_required
def profile_unfollow(request, username):
    """Отписаться от автора."""
    author = get_object_or_404(User, username=username)
    user = request.user
    unfollow = Follow.objects.filter(
        user_id=user.pk,
        author_id=author.pk)
    unfollow.delete()
    context = {
        'page_obj': post_paginator(
            request,
            get_following_authors_post_list(user))
    }

    return render(request, 'posts/follow.html', context)
