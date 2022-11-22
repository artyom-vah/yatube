from http import HTTPStatus
from django.test import TestCase, Client
from posts.models import Post, Group, User


class PostModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Artyom')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',)
        cls.post = Post.objects.create(
            id=100,
            author=cls.user,
            text='Тестовый пост',)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_guest_client_list(self):
        """Проверка всех url для неавторизованного пользователя."""
        guest_urls_list = [
            '/',
            '/group/test-slug/',
            '/profile/Artyom/',
            '/posts/100/',
        ]
        for guest_url in guest_urls_list:
            with self.subTest(address=guest_url):
                response = self.guest_client.get(guest_url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_authorized_client_list(self):
        """Проверка всех url для авторизованного пользователя."""
        guest_urls_lisе = [
            '/group/test-slug/',
            '/profile/Artyom/',
            '/posts/100/',
            '/create/',
        ]
        for guest_url in guest_urls_lisе:
            with self.subTest(address=guest_url):
                response = self.authorized_client.get(guest_url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authorized_post_edit_url(self):
        """Проверка url post_edit redirect для неавторизованного
        пользователя."""
        response = self.guest_client.get('/posts/100/edit/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/posts/100/edit/')

    def test_urls_posts_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/Artyom/': 'posts/profile.html',
            '/posts/100/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/100/edit/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_page_404(self):
        '''Проверяем несуществующую страницу'''
        response = self.guest_client.get('/page404/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_template_for_page_404(self):
        """кастомный шаблон для страницы 404"""
        response = self.guest_client.get('/page404/')
        self.assertTemplateUsed(response, 'core/404.html')
