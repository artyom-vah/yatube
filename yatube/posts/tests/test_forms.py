from http import HTTPStatus
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User


class PostFormCreateTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Artyom')
        cls.user_not_author = User.objects.create_user(
            username='Неавтор')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        Post.objects.create(
            text='Пост тест',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.user = PostFormCreateTests.user
        self.unauthorized_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_validate_form_authorized_client_create_post(self):
        """Создание поста зарегистрированным пользователем."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Текст для формы',
            'group': 1,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'), data=form_data, follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response, reverse('posts:profile', kwargs={
                'username': self.user.username,
            })
        )
        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_validate_form_authorized_client_edit_post(self):
        """
        Валидная форма редактирует существующую запись в Post,
        не создавая новую запись
        """
        post_count = Post.objects.count()
        old_text = Post.objects.get(id=1).text
        old_author = Post.objects.get(id=1).author
        old_group = Post.objects.get(id=1).group
        form_data = {
            'text': 'Обновлённый текст',
            'group': self.group.id,
        }
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.group.id}),
            data=form_data,
            follow=True,
        )
        new_text = Post.objects.get(id=1).text
        new_author = Post.objects.get(id=1).author
        new_group = Post.objects.get(id=self.group.id).group
        self.assertNotEqual(old_text, new_text)
        self.assertEqual(old_author, new_author)
        self.assertEqual(old_group, new_group)
        self.assertEqual(post_count, Post.objects.count())

    def test_create_post_unauthorized(self):
        """
        Гость не может создать новый пост
        и его редиректит на страницу логина
        """
        post_count = Post.objects.count()
        form_data = {
            'text': 'Пост гостя',
            'group': 1,
        }
        response = self.unauthorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response,
            f'{reverse("users:login")}?next={reverse("posts:post_create")}',
        ),

        self.assertEqual(Post.objects.count(), post_count)

    def test_edit_post_unauthorized(self):
        """
        Гость не может редактировать пост в БД
        и его редиректит на страницу логина
        """
        post_count = Post.objects.count()
        old_text = Post.objects.get(id=1).text
        old_author = Post.objects.get(id=1).author
        old_group = Post.objects.get(id=1).group
        form_data = {
            'text': 'Пост гостя',
            'group': 1,
        }
        response = self.unauthorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': 1}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response,
            (
                f'{reverse("users:login")}?next='
                f'{reverse("posts:post_edit", kwargs = {"post_id":1})}'
            ),
        )

        self.assertEqual(Post.objects.count(), post_count)
        new_text = Post.objects.get(id=1).text
        new_author = Post.objects.get(id=1).author
        new_group = Post.objects.get(id=1).group
        self.assertEqual(old_text, new_text)
        self.assertEqual(old_author, new_author)
        self.assertEqual(old_group, new_group)

    def test_edit_post_not_avtor(self):
        """
        Редактирование поста не автором
        (пост не должен изменить значения полей)
        """
        not_author_client = Client()
        not_author_client.force_login(self.user_not_author)
        response = not_author_client.get(
            '/posts/1/edit/', follow=True
        )
        self.assertRedirects(
            response,
            '/posts/1/',
        )
