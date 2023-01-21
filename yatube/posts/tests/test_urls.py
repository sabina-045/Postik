from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache

from posts.models import Group, Post, User


class PostURLTests(TestCase):
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
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.new_authorized_client = Client()
        self.new_authorized_client.force_login(self.new_user)

    def test_public_urls_exists_at_desired_location(self):
        """Url oбщих страниц доступны любому пользователю."""
        public_pages = (
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.user.username}/',
            f'/posts/{self.post.id}/'
        )
        for page in public_pages:
            response = self.client.get(page)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url_exists_at_desired_location_authorized(self):
        """Url cтраницы /create/ доступен авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_url_exists_at_desired_location_for_author(self):
        """Url страницы /edit/ доступен автору поста."""
        self.authorized_client == self.post.author
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адреса приложения posts используют соответствующие шаблоны."""
        cache.clear()
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest("Ошибка в URL", address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_url_private_pages_redirect_guest_client(self):
        """Выполняется редирект при заходе гостевого клиента
        на приватные страницы """
        response = self.client.get('/create/', follow=True)
        self.assertRedirects(
            response,
            (reverse('users:login')
                + '?next='
                + reverse('posts:post_create'))
        )
        response = self.client.get(f'/posts/{self.post.id}/edit/', follow=True)
        self.assertRedirects(
            response,
            (reverse('users:login')
                + '?next='
                + reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        )

    def test_url_edit_post_redirect_not_author(self):
        """Выполняется редирект при попытке не автора редактировать пост"""
        self.new_authorized_client != self.post.author
        response = self.new_authorized_client.get(
            f'/posts/{self.post.id}/edit/'
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )

    def test_404_page_show_desire_template(self):
        """При отсутсвии запрошенной страницы демонстрируется
        переопределенный шаблон 404.html."""
        response = self.client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': 22}))
        self.assertTemplateUsed(response, 'core/404.html')
