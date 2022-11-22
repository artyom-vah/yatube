from django.test import TestCase
from ..models import Group, Post, User, FIRST_TEXT_STR_15


class PostModelTests(TestCase):
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
            text='Тестовый пост',
        )

    def test_models_have_correct_object_group(self):
        """Проверяем, что у модели group корректно работает __str__."""
        group = PostModelTests.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_models_have_correct_object_post(self):
        """Проверяем, что у модели post корректно работает __str__."""
        post = PostModelTests.post
        expected_object_name = post.text[:FIRST_TEXT_STR_15]
        self.assertEqual(expected_object_name, str(post))

    def test_verbose_name_post(self):
        """verbose_name в полях совпадает с ожидаемым модели post."""
        post = PostModelTests.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Сообщество',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_verbose_name_group(self):
        """verbose_name в полях совпадает с ожидаемым модели group."""
        group = PostModelTests.group
        field_verboses = {
            'title': 'Имя',
            'slug': 'Адрес',
            'description': 'Описание',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)
