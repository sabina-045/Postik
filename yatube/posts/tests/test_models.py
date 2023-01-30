from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Основной тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей post и group
        корректно работает __str__."""
        expected_str = {
            self.post: self.post.text,
            self.group: self.group.title,
        }
        for object, expected_value in expected_str.items():
            with self.subTest(object=object):
                self.assertEqual(str(object), expected_value)

    def test_models_have_correct_verbose_names(self):
        """Проверяем, что у моделей post и group
        правильно отображается verbose_name."""
        expected_verbose = {
            self.post: "Пост группы",
            self.group: "Группа",
        }
        for object, expected_value in expected_verbose.items():
            with self.subTest(object=object):
                self.assertEqual(
                    object._meta.verbose_name, expected_value
                )

    def test_models_have_correct_help_text(self):
        """Проверяем, что у полей модели post
        правильно отображается help_text."""
        expected_help_text = {
            'text': "Напишите здесь что-нибудь умное",
            'group': "Группа, к которой будет относиться пост",
        }
        for field, expected_value in expected_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text, expected_value
                )
