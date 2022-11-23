from django.urls import reverse
from posts.models import Post, Group, User
from django.test import TestCase, Client


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Artyom')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',)

        posts_list = []
        for i in range(13):
            posts_list.append(Post(
                text=f'Текстовый текст {i}',
                author=cls.user,
                group=cls.group,
            ))
        cls.post = Post.objects.bulk_create(posts_list)

    def setUp(self):
        self.user = PaginatorViewsTest.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_first_page_contains_ten_records(self):
        """Проверка, паджинатор выводит 10 записей на страницу index"""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_index_second_page_contains_two_records(self):
        """Проверка, паджинатор выводит 4 записи на 2ю страницу index"""
        response = self.authorized_client.get(
            (reverse('posts:index') + '?page=2')
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_list_first_page_contains_ten_records(self):
        """Проверка, паджинатор выводит 10 записей на страницу group_list"""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_list_second_page_contains_two_records(self):
        """Проверка, паджинатор выводит 4 записи на 2ю страницу group_list"""
        response = self.authorized_client.get(
            (reverse('posts:group_list', kwargs={'slug': 'test-slug'}))
            + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_profile_first_page_contains_ten_records(self):
        """Проверка, паджинатор выводит 10 записей на страницу profile"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'Artyom'})
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_second_page_contains_two_records(self):
        """Проверка, паджинатор выводит 4 записи на 2ю страницу profile"""
        response = self.authorized_client.get(
            (
                reverse('posts:profile', kwargs={'username': 'Artyom'})
                + '?page=2'
            )
        )
        self.assertEqual(len(response.context['page_obj']), 3)
