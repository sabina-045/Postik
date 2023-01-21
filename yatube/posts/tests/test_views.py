import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post, User

from .. import constants
from .utils import get_temporary_image

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Noname')
        cls.new_user = User.objects.create_user(username='Another_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test2-slug',
            description='Тестовое описание группы2',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=get_temporary_image()
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            text='Тестовый комментарий',
            post=cls.post
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.new_authorized_client = Client()
        self.new_authorized_client.force_login(self.new_user)

    def check_context_form(self, response):
        """Проверяем форму из контекста"""
        form = response.context['form']
        self.assertTrue(len(form.fields) == 3)
        self.assertIn('group', form.fields.keys())
        self.assertIn('text', form.fields.keys())
        self.assertIn('image', form.fields.keys())

    def check_page_post_fields(self, response, post=bool):
        """Проверяем атрибуты поста из словаря context."""
        if post:
            post = response.context['post']
        else:
            post = response.context['page_obj'][0]
        self.assertEqual(post.id, self.post.pk)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.image, self.post.image)

    def test_pages_uses_correct_template(self):
        """URL-адрес 'name' использует соответствующий шаблон."""
        cache.clear()
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user.username}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
                'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
                'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest("Ошибка в имени пути",
                              reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_create_page_show_correct_context(self):
        """Шаблон create_post при создании поста
        сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_create')
        )
        self.check_context_form(response)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон create_post при редактировании поста
        сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        self.check_context_form(response)
        post = response.context['post']
        self.assertEqual(post.id, self.post.pk)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group, self.post.group)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id}))
        )
        self.check_page_post_fields(response, True)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        self.check_page_post_fields(response, False)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': self.user.username}))
        self.check_page_post_fields(response, False)
        author = response.context['author']
        self.assertEqual(author.id, self.post.author.pk)
        self.assertEqual(author.username, self.user.username)

    def test_group_posts_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug}))
        self.check_page_post_fields(response, False)
        group = response.context['group']
        self.assertEqual(group.id, self.group.pk)
        self.assertEqual(group.title, self.group.title)
        self.assertEqual(group.slug, self.group.slug)
        self.assertEqual(group.description, self.group.description)

    def test_post_create_show_correct_group(self):
        """Созданный пост отображается в ожидаемой группе,
           на страницах index, profile, group_list"""
        cache.clear()
        post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=self.group
        )
        responsed_pages = [
            reverse('posts:index'),
            reverse('posts:profile', kwargs={'username': self.user.username}),
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        ]
        for page in responsed_pages:
            response = self.authorized_client.get(page)
            post_list = response.context['page_obj']
            self.assertIn(post, post_list,
                          f'Пост отсутствует на странице {page}')
            self.assertEqual(response.context['page_obj'][0].id, post.id,
                             f'Пост отсутствует на 1 позиции страницы {page}')

    def test_post_create_doesnt_show_incorrect_group(self):
        """Созданный пост не отобразился в посторонней группе"""
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.group2.slug})
        )
        post_list = response.context['page_obj']
        self.assertNotIn(self.post, post_list,
                         'Пост отобразился в посторонней группе')

    def test_page_post_detail_show_created_comment(self):
        """Успешно отправленный комментарий появился
        на странице post_detail."""
        list_old_comments_id = list(
            Comment.objects.values_list('pk', flat=True)
        )
        form_data = {
            'text': 'Новый тестовый комментарий',
        }
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.id}
            ),
            data=form_data,
            follow=True
        )
        created_comment_amount = (
            Comment.objects.exclude(pk__in=list_old_comments_id)
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(created_comment_amount.count(), 1)
        created_comment = created_comment_amount.get()
        self.assertEqual(created_comment.text, form_data['text'])
        self.assertEqual(created_comment.author, self.user)
        response2 = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id})
        )
        self.assertIn(created_comment, response2.context['comments'],
                      'Комментарий не появился на странице поста')

    def test_authorized_client_can_follow_another_user(self):
        """Авторизованный пользователь может подписываться
        на других пользователей."""
        response = self.new_authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user.username})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(
            Follow.objects.filter(
                author_id=self.user.id,
                user_id=self.new_user.id).exists(),
            'Авторизованный клиент не смог подписаться на автора'
        )

    def test_authorized_client_can_unfollow_another_user(self):
        """Авторизованный пользователь может отписываться
        от других пользователей."""
        Follow.objects.create(
            author_id=self.user.id,
            user_id=self.new_user.id
        )
        response = self.new_authorized_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.user.username})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFalse(
            Follow.objects.filter(
                author_id=self.user.id,
                user_id=self.new_user.id).exists(),
            'Авторизованный клиент не смог отписаться на автора'
        )

    def test_author_new_post_appears_follower_posts_list(self):
        """Новый пост автора появляется в ленте постов
        подписавшегося пользователя."""
        Follow.objects.create(
            author_id=self.user.id,
            user_id=self.new_user.id
        )
        new_post = Post.objects.create(
            author=self.user,
            text='Проверяем наличие поста в ленте',
            group=self.group
        )
        response = self.new_authorized_client.get(
            reverse('posts:follow_index'))
        post_list = response.context['page_obj']
        self.assertIn(
            new_post,
            post_list,
            'Пост отсутствует в ленте подписчика')
        self.assertEqual(
            response.context['page_obj'][0].id,
            new_post.id,
            'Пост отсутствует на 1 позиции ленты подписчика')

    def test_author_new_post_absent_post_list_unfollow_user(self):
        """Новый пост автора не появляется в ленте постов
        не подписавшегося пользователя."""
        new_post = Post.objects.create(
            author=self.user,
            text='Проверяем отсутствие поста в ленте',
            group=self.group
        )
        response = self.new_authorized_client.get(
            reverse('posts:follow_index'))
        post_list = response.context['page_obj']
        self.assertNotIn(
            new_post,
            post_list,
            'Пост появился в ленте неподписавшегося пользователя')

    def test_cache_index_page(self):
        """При вызове index.html данные сохраняются в кэш."""
        new_post = Post.objects.create(
            author=self.user,
            text='Проверяем кэш',
            group=self.group
        )
        response = self.client.get(reverse('posts:index'))
        content = response.content
        response2 = self.client.get(reverse('posts:index'))
        self.assertEqual(content, response2.content)
        cache.clear()
        response3 = self.client.get(reverse('posts:index'))
        context = response3.context['page_obj']
        self.assertIn(new_post, context)
        self.assertNotEqual(response2.content, response3.content)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='Noname')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.bulk_create(
            [Post(
                text=post_num,
                author=cls.user,
                group=cls.group)
                for post_num in range(constants.NUMBER_OF_TEST_POSTS)]
        )

    def list_url_names(self):
        """Список запрошенных страниц index, profile, group_list"""
        responsed_pages = [
            reverse('posts:index'),
            reverse('posts:profile', kwargs={'username': self.user.username}),
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        ]

        return responsed_pages

    def test_first_page_contains_ten_records(self):
        """Paginator передает 10 постов на 1 страницу"""
        cache.clear()
        responsed_pages = self.list_url_names()
        for page in responsed_pages:
            response = self.client.get(page)
            self.assertEqual(len(
                response.context['page_obj']),
                constants.PAGE_POSTS_NUMBER
            )

    def test_first_page_contains_three_records(self):
        """Paginator передает 3 поста на 2 страницу"""
        cache.clear()
        responsed_pages = self.list_url_names()
        for page in responsed_pages:
            response = self.client.get(page + '?page=2')
            self.assertEqual(len(
                response.context['page_obj']),
                constants.NUMBER_OF_POSTS_FOR_PAGE_2
            )
