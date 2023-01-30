import shutil
import tempfile
from http import HTTPStatus

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings

from posts.models import Group, Post, User, Comment
from .utils import get_temporary_image, get_temporary_image_new

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Noname')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Основной тестовый пост',
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Новый пост появляется в базе данных"""
        list_old_posts_id = list(Post.objects.values_list('pk', flat=True))
        form_data = {
            'text': 'Новый тестовый пост',
            'group': self.group.id,
            'image': get_temporary_image()
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        new_post_amount = Post.objects.exclude(pk__in=list_old_posts_id)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(new_post_amount.count(), 1)
        new_post = new_post_amount.get()
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': self.post.author})
        )
        self.assertEqual(new_post.text, form_data['text'])
        self.assertEqual(new_post.group.id, form_data['group'])
        self.assertEqual(new_post.image, 'posts/small.gif')
        self.assertEqual(new_post.author, self.post.author)

    def test_edit_post_change(self):
        """При редактировании поста происходит его изменение в базе данных."""
        form_data = {
            'text': 'Измененный старый пост',
            'group': self.group.id,
            'image': get_temporary_image_new()
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(
            Post.objects.filter(
                id=self.post.id,
                author=self.post.author,
                text=form_data['text'],
                group=form_data['group'],
                image='posts/small_new.gif').exists(),
            'Данные поста не изменились'
        )

    def test_authorized_client_only_can_comment_post(self):
        """Только авторизованный пользователь может оставлять комментарий."""
        form_data = {
            'text': 'Новый тестовый комментарий',
        }
        response = self.client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.id}
            ),
            data=form_data,
            follow=True
        )
        comments = Comment.objects.all()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            len(comments),
            0,
            'Неавторизованный пользователь оставил комментарий'
        )

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
